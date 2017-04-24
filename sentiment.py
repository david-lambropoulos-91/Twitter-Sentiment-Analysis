import tweepy   # Needed for Twitter API
from pycorenlp import StanfordCoreNLP # Needed for sentiment analysis
from subprocess import Popen

def start_connection():
    # On unix
    #Popen("cd stanford-corenlp-full-2016-10-31; java -mx5g -cp \"*\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000", shell=True)
    
    # On windows
    Popen("cd stanford-corenlp-full-2016-10-31 & start /wait java -mx5g -cp \"*\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000",shell=True)

#def get_sentiment(phrases):

# Used for establishing connections to the Twitter API
class TwitterClient(object):
    
    # Constructor
    def __init__(self):
        # Twitter API Credentials keys/tokens
        consumer_key = ""
        consumer_secret = ""
        access_key = ""
        access_secret = ""

        # Attempt to authenticate
        try:
            # create OAuthHandler object
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

            # set access token and secret
            self.auth.set_access_token(access_key, access_secret)

            # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication failed.")
        
    def get_all_tweets(self, screen_name):
        #Twitter only allows access to a users most recent 3240 tweets with this method

        # initialize a list to hold all the tweepy Tweets
        alltweets = []

        # make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = self.api.user_timeline(screen_name = screen_name,count=200)

        # save most recent tweets
        alltweets.extend(new_tweets)

        # save the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        # keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
            print("getting tweets before %s" % (oldest))
    
            # all subsiquent requests use the max_id param to prevent duplicates
            new_tweets = self.api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)

            # save most recent tweets
            alltweets.extend(new_tweets)

            # update the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

            print("...%s tweets downloaded so far" % (len(alltweets)))

            # transform the tweepy tweets into a 2D array 
            outtweets = [[tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

        # print all posts on twitter   
        for post_info in outtweets:
            # grab post current as type byte b''
            raw_post = post_info[2] 
        
            # convert post from type byte to utf-8
            post_content = raw_post.decode("utf-8")
        
            # display post on the backend
            print("\n" + post_content + "\n")

def main():
    start_connection()
    #pass in the username of the account you want to download
    #get_all_tweets("realDonaldTrump")
    api = TwitterClient()
    api.get_all_tweets("realDonaldTrump")

if __name__ == '__main__':
    main()    
