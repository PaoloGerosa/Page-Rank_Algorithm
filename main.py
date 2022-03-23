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


articles = search("aba adhd")
print(articles)
print(len(articles))






















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