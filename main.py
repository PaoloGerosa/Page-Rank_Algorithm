from Class import *
from Credentials import *
from Auxiliary_Functions import *
from PubMed import *
from Twitter import *

## Call to the API of Twitter: Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


df = pd.read_csv("Users\paolo\OneDrive\Desktop\Page-Rank_Algorithm\Files\\Ukraine22_03_2022.csv")

search_term = "aba adhd"
g = twitter_graph(df, "Ukraine")
#g = pubmed_graph(search_term)
g.montecarlo()





