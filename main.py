# Import Libraries for Twitter and PubMed
from PubMed import *
from Twitter import *
from Tennis import *
from Auxiliary_Functions import load, personalized_altmetric, pca_analysis

# df = pd.read_csv("Files\\gasoil.csv")

search_term = "PageRank"
g = pubmed_graph(search_term)
# g = load(search_term, "pubmed")

# g.compare_order()

# g = twitter_graph(df, "Covid")
# print(find_standings(g.users, "2022-03-31", "2022-03-20", "covid_19"))

# df = pd.read_csv("Files\\2022.csv")
# g = tennis_graph(df, "tennis_2022")

# g.multiple_pagerank([g.personalized_vector, g.personalized_follower_vector, g.personalized_grass_vector])
g.montecarlo()
g.compute_standings()
print(g.myorder)


