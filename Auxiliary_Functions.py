import pickle
import tweepy

chomp = "C:\\Users\\paolo\\OneDrive\\Desktop\\Page-Rank-Algorithm\\Objects"

def save(filename, object):
    try:
        file_to_store = open(chomp + filename + ".pickle", "wb")
        pickle.dump(object, file_to_store)

        file_to_store.close()

    except Exception as ex:
        print("Error during storing data (Possibly unsupported):", ex)

def load(filename):
    try:
        file_to_read = open(chomp + filename + ".pickle", "rb")
        loaded_object = pickle.load(file_to_read)

        file_to_read.close()
        return loaded_object

    except Exception as ex:
        print("Error during loading data:", ex)


def find_standings(api, users, until, since, search):
    memo = dict()
    chomp = "until:" + until + " since:" + since
    public_tweets = tweepy.Cursor(api.search_tweets, q=search + chomp, result_type="mixed", tweet_mode="extended").items(2000)

    count = 1
    for aux, tweet in enumerate(public_tweets):
        if aux%100 == 0:
            print(aux)
        tweet_user = tweet.user
        name = "@"+tweet_user.screen_name
        if name in users:
            if name in memo:
                print("Repetition")
            memo[name] = count
            count += 1
    return memo



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