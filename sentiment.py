# sentiment.py
# Demonstrates connecting to the twitter API and accessing the twitter stream
# Author: Elia Eiroa
# Version 2.0
# Date: September 22, 2016

import twitter

# XXX: Go to http://dev.twitter.com/apps/new to create an app and get values
# for these credentials, which you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation.

print 'Establish Authentication Credentials'
CONSUMER_KEY = 'ucr3bax3IAMpi9fgbm0kZVUZJ'
CONSUMER_SECRET = 'QwurpSWEnM1mqhtv6G0GIxEmH4u59aapF6bs41WwtaluMUYn4q'
OAUTH_TOKEN = '775141100965142528-AWkId3e7XhWAyNcQPCcWrKoON1wFnZs'
OAUTH_TOKEN_SECRET = '6PJsimtin53k9NxFwjEUGseXgHfs7ALexKOzok742zd8J'

auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)

print "Nothing to see by displaying twitter_api except that it's now a defined variable"
print
print twitter_api
print
raw_input('Press Enter to continue...')
print

print "---------------------------------------------------------------------"
print 'Display world and US trends'
# The Yahoo! Where On Earth ID for the entire world is 1.
# See https://dev.twitter.com/docs/api/1.1/get/trends/place and
# http://developer.yahoo.com/geo/geoplanet/

WORLD_WOE_ID = 1
US_WOE_ID = 23424977

# Prefix ID with the underscore for query string parameterization.
# Without the underscore, the twitter package appends the ID value
# to the URL itself as a special case keyword argument.

world_trends = twitter_api.trends.place(_id=WORLD_WOE_ID)
us_trends = twitter_api.trends.place(_id=US_WOE_ID)
print 'Display World Trends'
print
print world_trends
print
print 'Display US trends'
print
print us_trends
print
raw_input('Press Enter to continue...')
print
print "---------------------------------------------------------------------"
print 'Displaying API responses as pretty-printed JSON '
print
raw_input("Press Enter to proceed... ")
print
import json
print
print 'World trends with json.dumps'
print json.dumps(world_trends, indent=1)
print
print
raw_input('Press Enter to continue...')
print
print 'US trends with json.dumps'
print json.dumps(us_trends, indent=1)
print
raw_input('Press Enter to continue...')
print
print "---------------------------------------------------------------------"
print 'Computing the intersection of two sets of trends'
world_trends_set = set([trend['name']
                        for trend in world_trends[0]['trends']])

us_trends_set = set([trend['name']
                     for trend in us_trends[0]['trends']])

common_trends = world_trends_set.intersection(us_trends_set)

print common_trends
print
print
print "---------------------------------------------------------------------"
print 'Collecting search results'
print
raw_input('Press Enter to continue...')
print
# Import unquote to prevent url encoding errors in next_results
from urllib import unquote

# XXX: Set this variable to a trending topic,
# or anything else for that matter. The example query below
# was a trending topic when this content was being developed
# and is used throughout the remainder of this chapter.

#GET THE USER IMPUTS FOR THE TWO TERMS THEY WANT TO SEARCH
q = raw_input('Enter your first search term: ')
q2 = raw_input('Enter your second search term: ')
print("Now calculating sentiment for the term: " + q)

#print q
#raw_input("Press Enter to continue")

count = 1000

# See https://dev.twitter.com/docs/api/1.1/get/search/tweets

search_results = twitter_api.search.tweets(q=q, count=count)

statuses = search_results['statuses']


# Iterate through 5 more batches of results by following the cursor

for _ in range(5):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e: # No more results when next_results doesn't exist
        break

    # Create a dictionary from next_results, which has the following form:
    # ?max_id=313519052523986943&q=NCAA&include_entities=1
    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

# Show one sample search result by slicing the list...
print json.dumps(statuses[0], indent=1)

print
raw_input("Press Enter to proceed... ")
print
print "---------------------------------------------------------------------"
print 'Extracting text, screen names, and hashtags from tweets'
print
raw_input("Press Enter to proceed... ")
print
status_texts = [ status['text']
                 for status in statuses ]

screen_names = [ user_mention['screen_name']
                 for status in statuses
                     for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text']
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]

# Compute a collection of all words from all tweets
words = [ w
          for t in status_texts
              for w in t.split() ]

# Explore the first 5 items for each...

print json.dumps(status_texts[0:5], indent=1)
print json.dumps(screen_names[0:5], indent=1)
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(words[0:5], indent=1)



print
raw_input("Press Enter to proceed...")
print
print "---------------------------------------------------------------------"
print 'Calculating lexical diversity for tweets'

# A function for computing lexical diversity
def lexical_diversity(tokens):
    return 1.0*len(set(tokens))/len(tokens)

# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ])
    return 1.0*total_words/len(statuses)
print 'Lexical diversity of words: '
print lexical_diversity(words)
print 'Lexical diversity of screen names: '
print lexical_diversity(screen_names)
print 'Lexical diversity of hashtags: '
print lexical_diversity(hashtags)
print 'Average number of words per tweet: '
print average_words(status_texts)

print
raw_input("Press Enter to proceed...")
print
print "---------------------------------------------------------------------"
print 'Looking up users who have retweeted a status'


# Get the original tweet id for a tweet from its retweeted_status node
# and insert it here in place of the sample value that is provided
# from the text of the book

_retweets = twitter_api.statuses.retweets(id=317127304981667841)
print [r['user']['screen_name'] for r in _retweets]


print
raw_input("Press Enter to proceed...")
print

print "---------------------------------------------------------------------"
print 'Sentiment analysis on the term: ' + q + ' has been calculated!'
sent_file = open('AFINN-111.txt')

scores = {} # initialize an empty dictionary
for line in sent_file:
    term, score  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
    scores[term] = int(score)  # Convert the score to an integer.

score = 0
for word in words:
    uword = word.encode('utf-8')
    if uword in scores.keys():
        score = score + scores[word]

#REPEAT FOR CALCULATIONS FOR SECOND TERM
print "Now doing an analysis on the term: " + q2
count = 1000

# See https://dev.twitter.com/docs/api/1.1/get/search/tweets

search_results = twitter_api.search.tweets(q=q2, count=count)

statuses = search_results['statuses']


# Iterate through 5 more batches of results by following the cursor

for _ in range(5):
    print "Length of statuses", len(statuses)
    try:
        next_results = search_results['search_metadata']['next_results']
    except KeyError, e: # No more results when next_results doesn't exist
        break

    # Create a dictionary from next_results, which has the following form:
    # ?max_id=313519052523986943&q=NCAA&include_entities=1
    kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])

    search_results = twitter_api.search.tweets(**kwargs)
    statuses += search_results['statuses']

# Show one sample search result by slicing the list...
print json.dumps(statuses[0], indent=1)

print
raw_input("Press Enter to proceed...")
print
print "---------------------------------------------------------------------"
print 'Extracting text, screen names, and hashtags from tweets'
print
raw_input("Press Enter to proceed...")
print
status_texts = [ status['text']
                 for status in statuses ]

screen_names = [ user_mention['screen_name']
                 for status in statuses
                     for user_mention in status['entities']['user_mentions'] ]

hashtags = [ hashtag['text']
             for status in statuses
                 for hashtag in status['entities']['hashtags'] ]

# Compute a collection of all words from all tweets
words = [ w
          for t in status_texts
              for w in t.split() ]

# Explore the first 5 items for each...

print json.dumps(status_texts[0:5], indent=1)
print json.dumps(screen_names[0:5], indent=1)
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(words[0:5], indent=1)



print
raw_input("Press Enter to proceed...")
print
print "---------------------------------------------------------------------"
print 'Calculating lexical diversity for tweets...'

# A function for computing lexical diversity
def lexical_diversity(tokens):
    return 1.0*len(set(tokens))/len(tokens)

# A function for computing the average number of words per tweet
def average_words(statuses):
    total_words = sum([ len(s.split()) for s in statuses ])
    return 1.0*total_words/len(statuses)
print 'Lexical diversity of words: '
print lexical_diversity(words)
print 'Lexical diversity of screen names: '
print lexical_diversity(screen_names)
print 'Lexical diversity of hashtags: '
print lexical_diversity(hashtags)
print 'Average number of words per tweet: '
print average_words(status_texts)

print
raw_input("Press Enter to proceed...")
print
print "---------------------------------------------------------------------"
print 'Looking up users who have retweeted a status.'


# Get the original tweet id for a tweet from its retweeted_status node
# and insert it here in place of the sample value that is provided
# from the text of the book

_retweets = twitter_api.statuses.retweets(id=317127304981667841)
print [r['user']['screen_name'] for r in _retweets]


print
raw_input("Press Enter to proceed...")
print

print "---------------------------------------------------------------------"
print 'Sentiment analysis on the term: ' + q2 + ' has been calculated!'
sent_file2 = open('AFINN-111.txt')

scores2 = {} # initialize an empty dictionary
for line in sent_file2:
    term, score2  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
    scores2[term] = int(score2)  # Convert the score to an integer.

score2 = 0
for word in words:
    uword = word.encode('utf-8')
    if uword in scores.keys():
        score2 = score2 + scores[word]

# PRINTS HIGHER SCORE
print
print "---------------------------------------------------------------------"
print "SENTIMENTAL ANALYSIS RESULTS:"
if score < score2:
    print(q2 + " has the higher sentiment value, with it being")
    print(score2)
    print("Compared to " + q + ", getting a score of")
    print(score)
else:
    print(q + " has the higher sentiment value, with it being")
    print(score)
    print("Compared to " + q2 + ", getting a score of")
    print(score2)
