import numpy as np
from copy import deepcopy
import random

class Graph:
    def __init__(self, df, mode = None, standings = None, threshold = 0):
        self.count = 0                              # Number of nodes in the graph
        self.inner_graph = dict()                   # Directed graph with inverted edges
        self.users = dict()                         # Elements of the graph associated to their indeces in the matrix
        self.reverse_users = []                     # Ordered users
        self.column_sums = []                       # Sums of the boolean elements in the columns to build markovmatrix
        self.invariant = []                         # Invariant probability distribution
        self.real_standings = standings             # Standings of objects in the real context (Twitter, Pubmed)
        self.myorder = []                           # My standings according to the algorithm
        self.combo_order = []                       # In PubMed Standings according to the algorithm combination of PageRank and Best Match sort
        self.links = dict()                         # When the network comes from PubMed it creates the links of the articles,
        self.authors = dict()                       # it creates the authors and descriptions for each article
        self.descriptions = dict()
        self.graph = dict()
        self.create_graph(df, mode, threshold)
        self.matrix = [[0 for _ in range(self.count)] for _ in range(self.count)]
        self.markovmatrix = []                      # Numpy matrix that represents the Google matrix
        self.create_adjacency_matrix()
        self.link = dict()

    # Given a source node and a target node it inserts their link in the graph
    def insert_node(self, source, target):
        if source:
            if source not in self.graph:
                self.graph[source] = set()
                self.inner_graph[source] = set()
                self.users[source] = self.count
                self.reverse_users.append(source)
                self.count += 1
            if target not in self.graph:
                self.graph[target] = set()
                self.inner_graph[target] = set()
                self.users[target] = self.count
                self.reverse_users.append(target)
                self.count += 1
            self.graph[source].add(target)
            self.inner_graph[target].add(source)
        else:
            if target not in self.graph:
                self.graph[target] = set()
                self.inner_graph[target] = set()
                self.users[target] = self.count
                self.reverse_users.append(target)
                self.count += 1

    # It creates the graph from a dataframe
    def create_graph(self, df, mode, threshold):
        new_df = df
        if mode:
            new_df = df.loc[df['Kind'] == mode]
        new_df = self.clean_df(threshold, new_df)
        for source, target in zip(new_df["Source"], new_df["Target"]):
            self.insert_node(source, target)

    # It removes from the dataframe all the nodes with number of backward link <= threshold
    def clean_df(self, threshold, df):
        seen = set()
        deletion = set()
        for user in df["Source"]:
            if user not in seen:
                count = df.loc[df.Source == user, 'Source'].count() + df.loc[df.Target == user, 'Target'].count()
                if count <= threshold:
                    deletion.add(user)
                seen.add(user)
        for elem in deletion:
            df = df.drop(df[df.Source == elem].index)
            df = df.drop(df[df.Target == elem].index)
        return df

    # It creates the adjacency matrix of the graph and it computes the Google matrix of the graph
    def create_adjacency_matrix(self):
        for source in self.graph:
            for target in self.graph[source]:
                self.matrix[self.users[target]][self.users[source]] = 1
        self.markovmatrix = np.array(deepcopy(self.matrix), dtype=float)
        self.column_sums = [sum([row[i] for row in self.matrix]) for i in range(self.count)]

        # 1st method
        for i in range(self.count):
            if not self.column_sums[i]:
                self.markovmatrix[:, i] = float(1 / self.count)
            else:
                for j in range(self.count):
                    if self.markovmatrix[j, i]:
                        self.markovmatrix[j][i] = float(1/self.column_sums[i])

    # Print some information of the graph
    def print_details(self):
        print("Total number of nodes: ", len(self.graph))

        dangling = 0
        for elem in self.column_sums:
            if not elem:
                dangling += 1

        print("Total number of dangling nodes: ", dangling)

    # It simulates a Montecarlo Random walk to approximate the invariant probability distribution of the matrix
    def montecarlo(self, show = 1, query = None):
        steps = 200000
        pi = np.array([0 for _ in range(self.count)])
        start_state = random.randint(0, self.count-1)
        pi[start_state] = 1
        prev_state = start_state
        alpha = 0.15
        beta = 0.3
        choice = [i for i in range(self.count)]
        if self.real_standings:
            query_words = set(query.split())
            personalized_vector = [0 for _ in range(self.count)]
            total = 0
            for i, elem in enumerate(self.real_standings):
                for word in query_words:
                    if word in elem:
                        personalized_vector[self.users[elem]] += beta
                personalized_vector[self.users[elem]] += float(1/(i+1))
                total += personalized_vector[self.users[elem]]
            personalized_vector = [val / total for val in personalized_vector]
        else:
            personalized_vector = [1/self.count for _ in range(self.count)]
        for i in range(steps):
            if (i%10000 == 0):
                print(i)
            threshold = random.random()
            if threshold < alpha:
                curr_state = np.random.choice(choice, p=personalized_vector)
            else:
                curr_state = np.random.choice(choice, p=self.markovmatrix[:,prev_state])
            pi[curr_state] += 1
            prev_state = curr_state

        self.invariant = pi/steps
        order = sorted(enumerate(self.invariant), key=lambda x: x[1], reverse=True)
        myorder = [self.reverse_users[order[i][0]] for i in range(self.count)]

        if self.real_standings:                      # Since the graph can consider more nodes than reality
            real_objects = set(self.real_standings)  # If there exists a real standing consider only same objects
            self.myorder = []
            for elem in myorder:
                if elem in real_objects:
                    self.myorder.append(elem)
        else:
            self.myorder = myorder

        if show:
            self.print_invariant(10)
        return self.invariant

    def compare_order(self):
        new_order = []
        for j in range(len(self.myorder)*2-1):
            for k in range(j+1):
                l = j-k
                if l < len(self.myorder) and k < len(self.myorder) and self.myorder[l] == self.real_standings[k]:
                    new_order.append(self.myorder[l])
        self.combo_order = new_order

        for i in range(10):
            print((self.real_standings[i], self.myorder[i], new_order[i]))


    # It prints the first k elements of the invariant probability distribution
    def print_invariant(self, k = 10):
        if not self.myorder or k > len(self.myorder):
            print("Error")
            return

        for i in range(k):
            print(self.myorder[i])

    # Only when the network is related to a PubMed query it creates a dictionary of all the links related to the URLs
    def add_info(self, memo_links, memo_authors, memo_descriptions):
        self.links = memo_links
        self.authors = memo_authors
        self.descriptions = memo_descriptions






