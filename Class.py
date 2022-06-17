import numpy as np
from copy import deepcopy
import random
import networkx as nx
import requests
from Auxiliary_Functions import personalized_altmetric, create_distribution

class Graph:
    def __init__(self, df, mode = None, threshold = 0):
        self.count = 0                              # Number of nodes in the graph
        self.inner_graph = dict()                   # Directed graph with inverted edges
        self.users = dict()                         # Elements of the graph associated to their indeces in the matrix
        self.reverse_users = []                     # Ordered users
        self.column_sums = []                       # Sums of the boolean elements in the columns to build markovmatrix
        self.invariant = []                         # Invariant probability distribution
        self.personalized_vector = []
        self.personalized_dict = dict()
        self.myorder = []                           # My standings according to the algorithm

        ## Graph data structures
        self.graph = dict()
        self.create_graph(df, mode, threshold)
        self.matrix = [[0 for _ in range(self.count)] for _ in range(self.count)]
        self.markovmatrix = []                      # Numpy matrix that represents the Google matrix
        self.create_adjacency_matrix()

    # It creates the graph from a dataframe
    def create_graph(self, df, mode, threshold):
        new_df = df
        if mode:
            new_df = df.loc[df['Kind'] == mode]
        new_df = self.clean_df(threshold, new_df)
        for source, target in zip(new_df["Source"], new_df["Target"]):
            self.insert_node(source, target)

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

    # It simulates a Montecarlo Random walk by using the networkx library
    def montecarlo_networkx(self):
        network = nx.Graph()
        network.add_nodes_from(list(self.users))
        edges = []
        for key, val in self.graph.items():
            for elem in val:
                edges.append([key, elem])
        network.add_edges_from(edges)
        invariant = nx.pagerank(network, personalization=self.personalized_dict)
        self.invariant = sorted(invariant.items(), key=lambda item: item[1], reverse=True)

    # It prints the first k elements of the invariant probability distribution
    def print_invariant(self, k=10):
        for i in range(min(k, len(self.myorder))):
            print(self.myorder[i])



api = "http://api.altmetric.com/v1/doi/"

# Subclass PubMed of the class Graph
class PubMed(Graph):
    def __init__(self, df, dict_of_publications, query, standings, mode = None, threshold = 0):
        super().__init__(df, mode, threshold)
        self.query = query
        self.publications = dict_of_publications
        self.real_standings = standings                     # Standings of objects in the real context (Twitter, Pubmed)
        self.combo_order = []                               # In PubMed Standings according to the algorithm combination of PageRank and Best Match sort
        self.multiple_order = []                            # Ranking with multiple pagerank algorithm

        self.add_info()
        self.altmetric_personalized_vector = personalized_altmetric(self)
        self.pubmed_personalized_vector = create_distribution(self, standings)
        self.compute_personalized()
        self.montecarlo()
        self.myorder = self.compute_standings()
        self.generalized_order = self.multiple_pagerank([self.altmetric_personalized_vector, self.pubmed_personalized_vector])
        self.combo_orders()

    def add_info(self):
        for article in self.publications:
            doi = self.publications[article].doi
            if doi:
                response = requests.get(api + doi)
                if response.status_code == 200:
                    result = response.json()
                    self.publications[article].details = result
                else:
                    print(doi)

    # It computes the probability distribution to be used in the Montecarlo simulation
    def compute_personalized(self):
        beta = 0.3
        query_words = set(self.query.split())
        personalized_vector = [0 for _ in range(self.count)]
        total = 0
        self.personalized_dict = dict(zip(self.users, [0] * len(self.users)))
        for i, elem in enumerate(self.real_standings):
            for word in query_words:
                if word in elem:
                    personalized_vector[self.users[elem]] += beta
                    self.personalized_dict[elem] += beta
            personalized_vector[self.users[elem]] += float(1 / (i + 1))
            self.personalized_dict[elem] += float(1 / (i + 1))
            total += personalized_vector[self.users[elem]]
        self.personalized_vector = [val / total for val in personalized_vector]

    def compute_standings(self, invariant = None):
        invariant = invariant if invariant is not None else self.invariant
        order = sorted(enumerate(invariant), key=lambda x: x[1], reverse=True)
        myorder = [self.reverse_users[order[i][0]] for i in range(self.count)]

        real_objects = set(self.real_standings)
        aux_myorder = []
        for elem in myorder:
            if elem in real_objects:
                aux_myorder.append(elem)
        return aux_myorder

    # It simulates a Montecarlo Random walk to approximate the invariant probability distribution of the matrix
    def montecarlo(self, show=1):
        steps = 200000
        pi = np.array([0 for _ in range(self.count)])
        start_state = random.randint(0, self.count - 1)
        pi[start_state] = 1
        prev_state = start_state
        alpha = 0.15
        choice = [i for i in range(self.count)]
        for i in range(steps):
            if (i % 10000 == 0):
                print(i)
            threshold = random.random()
            if threshold < alpha:
                curr_state = np.random.choice(choice, p=self.altmetric_personalized_vector)
            else:
                curr_state = np.random.choice(choice, p=self.markovmatrix[:, prev_state])
            pi[curr_state] += 1
            prev_state = curr_state

        self.invariant = pi / steps

        if show:
            self.print_invariant(10)
        return self.invariant

    def combo_orders(self):
        new_order = []
        for j in range(len(self.myorder) * 2 - 1):
            for k in range(j + 1):
                l = j - k
                if l < len(self.myorder) and k < len(self.myorder) and self.myorder[l] == self.real_standings[k]:
                    new_order.append(self.myorder[l])
        self.combo_order = new_order

    def compare_orders(self):
        for i in range(min(10, len(self.real_standings))):
            print((self.real_standings[i], self.myorder[i], self.combo_order[i]))

    def multiple_pagerank(self, personalized_list_vector):
        steps = 200000
        m = len(personalized_list_vector)
        pi = np.array([0 for _ in range(self.count)])
        start_state = random.randint(0, self.count - 1)
        pi[start_state] = 1
        prev_state = start_state
        alpha = 0.15
        gamma = alpha/m
        choice = [i for i in range(self.count)]
        for i in range(steps):
            threshold = random.random()
            if threshold < alpha:
                index = int(threshold // gamma)
                curr_state = np.random.choice(choice, p=personalized_list_vector[index])
            else:
                curr_state = np.random.choice(choice, p=self.markovmatrix[:, prev_state])
            pi[curr_state] += 1
            prev_state = curr_state

        invariant = pi / steps
        order = self.compute_standings(invariant)
        return order



# Subclass Twitter of the class Graph
class Twitter(Graph):
    def __init__(self, df, mode = None, threshold = 0):
        super().__init__(df, mode, threshold)

        self.compute_personalized()
        self.montecarlo_networkx()
        self.compute_standings()

    # It computes the probability distribution to be used in the Montecarlo simulation
    def compute_personalized(self):
        self.personalized_dict = dict(zip(self.users, [1/self.count] * len(self.users)))
        self.personalized_vector = [1/self.count for _ in range(self.count)]

    def compute_standings(self):
        order = sorted(enumerate(self.invariant), key=lambda x: x[1], reverse=True)
        self.myorder = [self.reverse_users[order[i][0]] for i in range(self.count)]




class Publication:
    def __init__(self, title, id, description, authors, doi):
        self.title = title
        self.id = id
        self.description = description
        self.authors = authors
        self.doi = doi
        self.details = None


