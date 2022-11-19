import numpy as np
from copy import deepcopy
import random
import requests
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from functools import cmp_to_key
from scipy.stats import geom
import pandas as pd

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
        self.real_standings = standings                     # Standings of objects in the real context
        self.combo_order = []                               # In PubMed Standings according to the algorithm combination of PageRank and Best Match sort

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
        if self.count:
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
        gamma = alpha / m
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



class Publication:
    def __init__(self, title, id, description, authors, doi):
        self.title = title
        self.id = id
        self.description = description
        self.authors = authors
        self.doi = doi
        self.details = None




## These are the functions to support the classes initiated above

# PCA analysis in order to personalize teleportation distribution
def pca_analysis(g):
    # features to use to create the standing
    columns = ['cited_by_feeds_count', 'cited_by_posts_count', 'cited_by_tweeters_count', 'cited_by_policies_count', 'cited_by_patents_count', 'cited_by_wikipedia_count', 'cited_by_accounts_count', 'score', 'readers_count', 'mendeley', 'connotea']
    # features that are under readers in the details of the publication
    sub_columns = ['mendeley', 'connotea']
    # articles that have non empty details
    articles_list = []
    article_dict = {col: [] for col in columns}
    for article in g.publications:
        details = g.publications[article].details
        if details:
            articles_list.append(article)
            for i, col in enumerate(columns):
                if col in sub_columns:
                    info = details["readers"].get(col, 0)
                else:
                    info = details.get(col, 0)
                article_dict[col].append(info)
    details_df = pd.DataFrame(data = article_dict)

    features = columns
    x = details_df.loc[:, features].values
    # Standardizing the features
    print(x)
    x = MinMaxScaler().fit_transform(x)

    pca = PCA(n_components=2)
    principalComponents = pca.fit_transform(x)
    return principalComponents, articles_list

# Comparison used to sort and create the standing
def compare(item1, item2):
    if item1[1] > item2[1] + 0.5:
        return 1
    elif item2[1] > item1[1] + 0.5:
        return -1
    else:
        if item1[2] > item2[2]:
            return 1
        elif item2[2] > item1[2]:
            return -1
    return 0

# It creates the standing and return the final personalized distribution
def personalized_altmetric(g):
    pc, articles_list = pca_analysis(g)
    pc = [[i, pc[i][0], pc[i][1]] for i in range(len(pc))]
    pc.sort(key=cmp_to_key(compare), reverse=True)
    standing = [pc[i][0] for i in range(len(pc))]
    return create_pca_distribution(g, standing, articles_list)

# It creates the geometric distribution to use in the Montecarlo simulation
def create_pca_distribution(g, standing, articles_list):
    X = [i+1 for i in range(len(standing))]
    p = 0.2
    geom_pd = geom.pmf(X, p)
    prob_left = 1 - sum(geom_pd)
    geom_standing = {articles_list[standing[i]]: geom_pd[i] for i in range(len(articles_list))}

    elements_left = g.count - len(geom_pd)
    personalized_vector = [float(prob_left / elements_left) if elements_left else 0 for _ in range(g.count)]
    for elem in geom_standing:
        personalized_vector[g.users[elem]] = geom_standing[elem]

    return personalized_vector

def create_distribution(g, standing):
    X = [i + 1 for i in range(len(standing))]
    p = 0.2
    geom_pd = geom.pmf(X, p)
    total_prob = sum(geom_pd)
    geom_standing = {standing[i]: geom_pd[i] for i in range(len(standing))}

    personalized_vector = [0.0 for _ in range(g.count)]
    for elem in geom_standing:
        personalized_vector[g.users[elem]] = float(geom_standing[elem] / total_prob)

    return personalized_vector





