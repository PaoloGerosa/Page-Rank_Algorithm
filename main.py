# Import Libraries for Twitter and PubMed
from PubMed import *
from Twitter import *

df = pd.read_csv("Files\\gasoil.csv")

search_term = "aba adhd"
# g = pubmed_graph(search_term)

# g = load("Covid", "twitter")

# g.compare_order()

g = twitter_graph(df, "Covid")
# print(find_standings(g.users, "2022-03-31", "2022-03-20", "covid_19"))