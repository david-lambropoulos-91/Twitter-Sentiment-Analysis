import tweepy   # Needed for Twitter API
from pycorenlp import StanfordCoreNLP # Needed for sentiment analysis
from subprocess import Popen
import sys
import re
import datetime

def start_connection():
    # On unix
    #Popen("cd stanford-corenlp-full-2016-10-31; java -mx5g -cp \"*\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000", shell=True)
    
    # On windows
    Popen("cd stanford-corenlp-full-2016-10-31 & start /wait java -mx5g -cp \"*\" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -timeout 10000",shell=True)

def get_sentiment(phrase):
    nlp = StanfordCoreNLP('http://localhost:9000')
    #print("Connected to http://localhost:9000") 
    res = nlp.annotate(phrase, properties={'annotators': 'sentiment','outputFormat': 'json', 'timeout': 10000,})
    
    n = 0
    sum = 0
    #print(phrase)
    for s in res["sentences"]:
        
        print("%d: '%s': %s %s" % (s["index"], " ".join([t["word"] for t in s["tokens"]]),
                s["sentimentValue"], s["sentiment"]))
        word = "%s" % (" ".join([t["word"] for t in s["tokens"]]))
        if word != '!' and word != '?' and word != '.':
            sum = sum + int(s["sentimentValue"])
            n = n + 1
    
    #print("n= %d, sum = %d" % (n,sum))
    if n == 0:
        n = n + 1
    return sum / n

def get_total_sentiment(phrases):
    n = 0
    sum = 0

    for phrase in phrases:
        n = n + 1
        sum = sum + get_sentiment(phrase)
    
    if n == 0:
        n = n + 1

    return sum / n

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
    
    def remove_hashtags_hyperlinks(self, tweet):
        clean_tweet = ""

        tokens = tweet.split( )

        for token in tokens:
            if token[0] == '#':
                pass
            elif token[0] == '@':
                pass
            elif re.search('^http', token):
                pass
            elif re.search('^bit.ly', token):
                pass
            elif re.search('^tinyurl', token):
                pass
            else:
                clean_tweet = clean_tweet + token + " "
        #print(clean_tweet)

        return clean_tweet

    def get_tweets(self, screen_name, duration = None):
        #Twitter only allows access to a users most recent 3240 tweets with this method

        # initialize a list to hold all the tweepy Tweets
        alltweets = []

        # list of actual tweets
        clean_tweets = []

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
            
            if duration is not None:
                # Obtain year-month-day string and compare
                if str(post_info[1]).split( )[0] <= duration:
                    return clean_tweets
    
            # grab post current as type byte b''
            raw_post = post_info[2] 
            
            # convert post from type byte to utf-8
            post_content = raw_post.decode("utf-8")
            
            # display post on the backend
            #print(post_content + "\n")
            
            clean_tweet = self.remove_hashtags_hyperlinks(post_content)
            
            if(clean_tweet == ''):
                pass
            elif len(clean_tweet) == 1 and clean_tweet == '!':
                pass
            elif len(clean_tweet) == 1 and clean_tweet == '.':
                pass
            else:
                clean_tweets.append(clean_tweet)

        return clean_tweets

# Find the destination date
def destination_date(num_days_ago):
    return str(datetime.datetime.now()-datetime.timedelta(days=num_days_ago)).split( )[0]

# Display correct usage of program
def usage():
    print("Correct usage: python sentiment.py <twitter handle>")
    print("               python sentiment.py <twitter handle> -t <days>")
    print("Example: python sentiment.py realDonaldTrump")

def main(argc,argv):

    # get the date to stop looking at tweets
    stop_date = destination_date(int(argv[3]))

    # start Standford NLP Core
    start_connection()

    # pass in the username of the account you want to download
    api = TwitterClient()
    if argc != 4:
        tweets = api.get_tweets(argv[1])
    else:
        tweets = api.get_tweets(argv[1], stop_date)

    print("Attempting sentiment")

    # Calculate and display the sentiment of the tweets
    print("Total sentiment value: %f" % (get_total_sentiment(tweets))) 

if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
        sys.exit()
    elif len(sys.argv) == 3:
        if sys.argv[2] == '-t':
            print("Error: no argument provided to %s" % (sys.argv[2]))
            usage()
            sys.exit()
        else:
            print("Error: %s is not a correct argument" % (argv[2]))
            usage()
            sys.exit()
    elif len(sys.argv) > 4:
        print("Error: Too many arguments!")
        usage()
        sys.exit()

    try:
        main(len(sys.argv),sys.argv)
    except Exception as e:
        print("Error encountered: %s" % (e))
        sys.exit()
