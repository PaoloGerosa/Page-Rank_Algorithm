from Class import *
from Credentials import *
from Auxiliary_Functions import *
from PubMed import *

## Call to the API of Twitter: Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

"""
df = pd.read_csv("Users\paolo\OneDrive\Desktop\Page-Rank_Algorithm\Files\\Ukraine22_03_2022.csv")

## mode = Retweet, Quote, Mention, Retweets
g = Graph()
g.create_graph(df, mode = "Quote", threshold = 0)
save("Ukraine", g)

g = load("Ukraine")
g.print_details()



invariant = g.montecarlo()
invariant = sorted(enumerate(invariant), key = lambda x: x[1], reverse = True)
print(invariant[:5])

for i in range(10):
    try:
        user_name = api.get_user(screen_name = g.reverse_users[invariant[i][0]]).name
        print(user_name)
    except: pass

"""

"""
link = constructLink("aba adhd", 1)
soup = get_soup(link)
text = soup.body.main.find('div', class_='inner-wrap')
text = text.find('find', class_="search-results")
print(text)
"""







