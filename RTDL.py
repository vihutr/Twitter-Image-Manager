#!/usr/bin/env python
# encoding: utf-8

import tweepy #https://github.com/tweepy/tweepy
from decouple import config
import urllib
import requests
from bs4 import BeautifulSoup
import csv
import re
from TwitterAPI import TwitterAPI

#Twitter API credentials
consumer_key = config('consumer_key')
consumer_secret = config('consumer_secret')
access_key = config('access_key')
access_secret = config('access_secret')
bearer_token = config('bearer_token')

test_username = config('test_username')




def get_tweets(screen_name):
    print("Authorizing...")
    # Version 2 Endpoint
    api = TwitterAPI(consumer_key, consumer_secret, access_key, access_secret, api_version='2')
    print("Authorized!")
    print("Searching...")
    USER_ID = 0
    r = api.request(f'users/by/username/:{screen_name}')
    for item in r:
        print("User found!")
        print(item)
        USER_ID = item['id']

    # rx = re.compile(r"(https://[^ ]+)")

    # Get tweets - default setting
    print("Get tweets - default setting")
    params = {'max_results': 5, 'tweet.fields': 'created_at', }
    tweets = api.request(f'users/:{USER_ID}/tweets', params)
    imgcnt = 0
    for i, t in enumerate(tweets):
        print(str(i) + "   id: " + t['id'])
        tweetmatch = re.search("(?P<url>https?://[^\s]+)", t['text'])
        if tweetmatch:
            turl = tweetmatch.group(0)
            print("   url: " + turl)
            #req = requests.get(turl)#, headers = {'HEADERS GO HERE'})
            #bs = BeautifulSoup(req.content, 'html.parser')
            #print(bs.prettify())
            #imgUrl = bs.find('img', attrs={'alt': 'Embedded image permalink'}).get('src')
            #urllib.urlretrieve(imgUrl, "cnn.jpg")
        imgcnt += 1
        #print(rx.sub(r'<a href="\1">\1</a>', t['text']))=

    '''
    # Get tweets with customization - (5 tweets only with created_at timestamp)
    print("\nGet tweets with customization - (5 tweets only with created_at timestamp)")
    params = {'max_results': 5, 'tweet.fields': 'created_at'}
    tweets = api.request(f'users/:{USER_ID}/tweets', params)
    for t in tweets:
        print(t['text'])
        
    # Get next 5 tweets
    print("\nGet next 5 tweets")
    next_token = tweets.json()['meta']['next_token']
    params = {'max_results': 5, 'tweet.fields': 'created_at', 'pagination_token': next_token}
    tweets = api.request(f'users/:{USER_ID}/tweets', params)
    for t in tweets:
        print(t['text'])
    '''
    #print(r.get_quota())
    

    '''
    r = api.request(f'tweets/:{TWEET_ID}', 
		{
			'expansions':EXPANSIONS, 
			'media.fields':MEDIA_FIELDS
		})
    for item in r:
        print(json.dumps(item, indent=2))
    print(r.get_quota())
    '''

    '''
    #Twitter only allows access to a users most recent 3240 tweets with this method
    #authorize twitter, initialize tweepy
    print("Initializing tweepy")
    print("Authorizing tweepy...")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    print("Tweepy Authorized")
    print("Starting tweepy client...")
    client = tweepy.Client(bearer_token=bearer_token)
    print("Tweepy client started")
    '''


    '''
    # https://github.com/twitterdev/getting-started-with-the-twitter-api-v2-for-academic-research/blob/main/modules/5-how-to-write-search-queries.md
    query = 'from:'+screen_name+' is:retweet'
    
    tweets = client.search_recent_tweets(query=query, tweet_fields=['context_annotations','created_at'],
                                     media_fields=['preview_image_url'], expansions='attachments.media_keys',
                                    max_results=10)
    
    # Get list of media from the includes object
    media = {m["media_key"]: m for m in tweets.includes['media']}

    
    print(tweets.includes)
    for tweet in tweets.data:
        attachments = tweet.data['attachments']
        media_keys = attachments['media_keys']
        #print(tweet.text)
        #print(media)
        #print(media_keys)
        #print(media[media_keys[0]])
        if media[media_keys[0]].preview_image_url:
            print(media[media_keys[0]].preview_image_url)
    

    for tweet in tweets.data:
        print("for tweets in data")
        attachments = tweet.data['attachments']
        media_keys = attachments['media_keys']
        if media[media_keys[0]].type == photo:
            print("photo")
            print(media[media_keys[0]].preview_image_url)
            r = requests.get(media[media_keys[0]].preview_image_url)
            bs = BeautifulSoup(r.content, 'html.parser')
            imgUrl = bs.find('img', attrs={'alt': 'Embedded image permalink'}).get('src')
            print("URL" + imgUrl)
            local_filename, headers = urllib.urlretrieve(imgUrl)
            print(local_filename)

            #urllib.request.urlretrieve(media[media_keys[0]].preview_image_url + "", )
        #print(tweet)
    '''

    '''
    #initialize a list to hold all the tweepy Tweets
    alltweets = []
    
    #make initial request for most recent tweets (200 is the maximum allowed count)
    #new_tweets = api.user_timeline(screen_name = screen_name,count=10)
    print("Tweets")
    print(new_tweets)
    
    #save most recent tweets
    alltweets.extend(new_tweets)
    
    #save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
    print("Oldest id: " + oldest)
    
    #keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print(f"getting tweets before {oldest}")
        
        #all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
        
        #save most recent tweets
        alltweets.extend(new_tweets)
        
        #update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
        print(f"...{len(alltweets)} tweets downloaded so far")
    
    #transform the tweepy tweets into a 2D array that will populate the csv 
    outtweets = [[tweet.id_str, tweet.created_at, tweet.text] for tweet in alltweets]
    '''
    #write the csv  
    '''
    with open(f'new_{screen_name}_tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id","created_at","text"])
        writer.writerows(outtweets)
    '''
    #print(outtweets)
    
    pass

'''
def getTweets():
    api = twitter.Api(consumer_key = consumer_key, consumer_secret = consumer_secret, access_token_key = access_key, access_token_secret = access_secret, )
    results = api.GetSearch(raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")
    print(results)'''


if __name__ == '__main__':
	#pass in the username of the account you want to download
	get_tweets(test_username)
