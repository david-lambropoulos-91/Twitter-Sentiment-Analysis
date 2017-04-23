import tweepy   # Needed for Twitter API
from pycorenlp import StanfordCoreNLP # Needed for sentiment analysis
from subprocess import call


# Twitter API Credentials
consumer_key = ""
consumer_secret = ""
access_key = ""
access_secret = ""


def get_sentiment():
    call("../../Downloads/stanford-corenlp-full-2016-10-31/stanford-corenlp-full-2016-10-31/java -mx5g -cp \"*\" edu.stanford.nlp.pipline.StanfordCoreNLPServer -timeout 10000")


def get_all_tweets(screen_name):
    #Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))

        # transform the tweepy tweets into a 2D array 
        outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

    #print(alltweets)

    # print all posts on twitter   
    for post_info in outtweets:
        # grab post current as type byte b''
        raw_post = post_info[2] 
        
        # convert post from type byte to utf-8
        post_content = raw_post.decode("utf-8")
        
        # display post on the backend
        #print("\n" + post_content + "\n")

if __name__ == '__main__':
    #pass in the username of the account you want to download
    get_all_tweets("realDonaldTrump")
    get_sentiment()
