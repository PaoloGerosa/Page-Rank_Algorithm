# Import Libraries for Twitter and PubMed
from PubMed import *
from Twitter import *


df = pd.read_csv("Users\paolo\OneDrive\Desktop\Page-Rank_Algorithm\Files\\Ukraine22_03_2022.csv")

search_term = "aba adhd"
# g = twitter_graph(df, "Ukraine")
g = pubmed_graph(search_term)
g.montecarlo()





