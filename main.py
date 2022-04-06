# Import Libraries for Twitter and PubMed
from PubMed import *
from Twitter import *
from Auxiliary_Functions import *


df = pd.read_csv("Files\\covid_19.csv")

search_term = "applied behavior analysis aba"
# g = pubmed_graph(search_term)

g = load("applied behavior analysis", "pubmed")
g.compare_order()

# g = twitter_graph(df, "Covid")
# print(find_standings(g.users, "2022-03-31", "2022-03-20", "covid_19"))