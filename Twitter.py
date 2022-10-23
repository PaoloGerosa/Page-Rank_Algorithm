# Import Libraries to create a Graph object and to save it in local
from Class import Twitter
from Auxiliary_Functions import save
from Credentials import *

# It generates a Graph object using a twitter dataframe derived from Gephi
def twitter_graph(df, save_term, threshold = 0):
    g = Twitter(df = df, mode = "Quote", threshold = threshold)
    save(save_term, g, "twitter")

    g.print_details()
    return g

# Return the standing of users available in the first 2000 tweets according to Twitter
def find_standings(users, until, since, search):
    memo = dict()
    chomp = " until:" + until + " since:" + since
    public_tweets = tweepy.Cursor(api.search_tweets, q=search + chomp, result_type="mixed", tweet_mode="extended").items(10000)

    count = 1
    for aux, tweet in enumerate(public_tweets):
        if aux%100 == 0:
            print(aux)
        tweet_user = tweet.user
        name = "@"+tweet_user.screen_name
        if name in users and name not in memo:
            memo[name] = count
            count += 1
    return memo








# Tentative functions for Twitter scraping; inefficient!!

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



"""
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
"""



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


