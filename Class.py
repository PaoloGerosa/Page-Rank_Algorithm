import numpy as np
from copy import deepcopy
import random

class Graph:
    def __init__(self, graph = None, df = None, mode = None):
        self.count = 0
        self.matrix = []
        self.markovmatrix = []
        self.inner_graph = dict()
        self.users = dict()
        self.reverse_users = []
        self.column_sums = []
        self.invariant = []
        if not graph:
            self.graph = self.create_graph(df, mode)
        else:
            self.graph = graph
            self.save_users()
            self.matrix = [[0 for _ in range(self.count)] for _ in range(self.count)]
        self.create_adjacency_matrix()

    def save_users(self):
        for source in self.graph:
            if source not in self.users:
                self.inner_graph[source] = set()
                self.users[source] = self.count
                self.reverse_users.append(source)
                self.count += 1
            for target in self.graph[source]:
                if target not in self.users:
                    self.inner_graph[target] = set()
                    self.users[target] = self.count
                    self.reverse_users.append(target)
                    self.count += 1
                self.inner_graph[target].add(source)

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

    def create_graph(self, df, mode, threshold = 1):
        new_df = df.loc[df['Kind'] == mode]
        new_df = self.clean_df(threshold, new_df)
        for source, target in zip(new_df["Source"], new_df["Target"]):
            self.insert_node(source, target)

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

    def print_details(self):
        print("Total number of nodes: ", len(self.graph))

        dangling = 0
        for elem in self.column_sums:
            if not elem:
                dangling += 1

        print("Total number of dangling nodes: ", dangling)

    def montecarlo(self):
        steps = 200000
        pi = np.array([0 for _ in range(self.count)])
        start_state = random.randint(0, self.count-1)
        pi[start_state] = 1
        prev_state = start_state
        alpha = 0.15
        choice = [i for i in range(self.count)]
        for i in range(steps):
            if (i%10000 == 0):
                print(i)
            threshold = random.random()
            if threshold < alpha:
                curr_state = random.randint(0, self.count-1)
            else:
                curr_state = np.random.choice(choice, p=self.markovmatrix[:,prev_state])
            pi[curr_state] += 1
            prev_state = curr_state

        self.invariant = pi/steps
        return self.invariant




"""
memo = dict()
public_tweets = tweepy.Cursor(api.search_tweets, q="#inter", result_type = "mixed", tweet_mode = "extended", until="2022-03-12", since="2022-03-11")\
                .items(2000)

count = 1
for aux, tweet in enumerate(public_tweets):
    if aux%100 == 0:
        print(aux)
    tweet_user = tweet.user
    name = "@"+tweet_user.screen_name
    if name in g.users:
        #if name in memo:
        #    print("Repetition")
        memo[name] = count
        count += 1
print(len(memo))

count = 0
for i, elem in enumerate(invariant[:10]):
    name, _ = elem
    if g.reverse_users[name] in memo:
        print(i)
        count += 1
print(count)


import twint
t = twint.Config()
t.Popular_tweets = True
t.Search = "#ukraine"

t.Pandas = True
t.Limit = 10

twint.run.Search(t)

Tweets_df = twint.storage.panda.Tweets_df
print(Tweets_df)
"""


