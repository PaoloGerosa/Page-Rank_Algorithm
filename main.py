# Import Libraries for Twitter and PubMed
from PubMed import *
from Twitter import *
from Auxiliary_Functions import load, personalized_altmetric, pca_analysis

df = pd.read_csv("Files\\gasoil.csv")

search_term = "denver autism"
g = pubmed_graph(search_term)
g = load(search_term, "pubmed")

# g.compare_order()

# g = twitter_graph(df, "Covid")
# print(find_standings(g.users, "2022-03-31", "2022-03-20", "covid_19"))
