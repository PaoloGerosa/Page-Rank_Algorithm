import numpy as np
from copy import deepcopy

class Graph:
    def __init__(self):
        self.graph = dict()
        self.inner_graph = dict()
        self.matrix = []
        self.markovmatrix = []
        self.users = dict()
        self.count = 0
        self.reverse_users = []
        self.column_sums = []
        self.invariant = []

    def insert_node(self, source, target):
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

    def create_graph(self, df, mode):
        new_df = df.loc[df['Kind'] == mode]
        for source, target in zip(new_df["Source"], new_df["Target"]):
            self.insert_node(source, target)
        self.matrix = [[0 for _ in range(self.count)] for _ in range(self.count)]
        self.create_adjacency_matrix()

    def create_adjacency_matrix(self):
        for source in self.graph:
            for target in self.graph[source]:
                self.matrix[self.users[target]][self.users[source]] = 1
        self.markovmatrix = np.array(deepcopy(self.matrix), dtype = float)
        self.column_sums = [sum([row[i] for row in self.matrix]) for i in range(self.count)]

        # 1st method
        for i in range(self.count):
            if not self.column_sums[i]:
                self.markovmatrix[:, i] = float(1 / self.count)
            else:
                for j in range(self.count):
                    if self.markovmatrix[j, i]:
                        self.markovmatrix[j][i] = float(1/self.column_sums[i])

        #2nd method
        """
        
        """


    def print_details(self):
        print("Total number of nodes: ", len(self.graph))

        dangling = 0
        for elem in self.column_sums:
            if not elem:
                dangling += 1

        print("Total number of dangling nodes: ", dangling)

    def montecarlo(self, start_state = 0):
        steps = 10000
        pi = np.array([0 for _ in range(self.count)])
        pi[start_state] = 1
        prev_state = start_state

        choice = [i for i in range(self.count)]
        for i in range(steps):
            curr_state = np.random.choice(choice, p=self.markovmatrix[:,prev_state])
            pi[curr_state] += 1
            prev_state = curr_state

        self.invariant = pi/steps
        return self.invariant


