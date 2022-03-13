from Class import *
from Credentials import *
import pandas as pd

## Call to the API of Twitter: Tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

"""
public_tweets = tweepy.Cursor(api.search_tweets, q="bitcoin", result_type="mixed", tweet_mode="extended").items(1000)
memo = dict()

for count, tweet in enumerate(public_tweets):
    tweet_text = tweet.full_text
    tweet_id = tweet.id
    retweets = api.get_retweeter_ids(tweet_id)
    memo[tweet_id] = retweets
    print(count)

print(memo)
"""

df = pd.read_csv("Users\paolo\OneDrive\Desktop\Page-Rank_Algorithm\\inter.csv")

## mode = Retweet, Quote, Mention, Retweets
g = Graph()
g.create_graph(df, mode = "Mention")
save("Inter_object", g)

# g = load("Russia_object")
g.print_details()

invariant = g.montecarlo(53)
invariant = sorted(enumerate(invariant), key = lambda x: x[1], reverse = True)
print(invariant[:5])

first, inner_first = "", set()
for i in range(10):
    try:
        user = api.get_user(screen_name = g.reverse_users[invariant[i][0]]).name
        if user in inner_first:
            print((user, i))
        print(user)
    except:
        user = None

    #print(len(g.inner_graph[g.reverse_users[invariant[i][0]]]))
    if not i:
        first = user
        inner_first = g.inner_graph[g.reverse_users[invariant[i][0]]]

memo = find_standings(api, g.users, "2022-03-12", "2022-03-10", "inter " )
print(len(memo))
print()




"""
public_tweets = tweepy.Cursor(api.search_tweets, q="bitcoin", result_type="mixed", tweet_mode="extended").items(10)
memo = dict()


for count, tweet in enumerate(public_tweets):
    user = tweet.user
    if not count:
        print(user)
        print(dir(user))

user = api.get_user(screen_name = '@lindah56')
print(user.screen_name)

print(g.users)
"""