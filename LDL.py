import requests
import os
import json
import pandas as pd
import sqlite3

from TwitterAPI import TwitterAPI
from decouple import config

#Twitter API credentials using virtual environment tokens
#consumer_key = config('consumer_key')
#consumer_secret = config('consumer_secret')
#access_key = config('access_key')
#access_secret = config('access_secret')
bearer_token = config('bearer_token')

testuid = config('test_user_id')

# To set your environment variables in terminal run the following:
# export 'BEARER_TOKEN'='<your_bearer_token>'

def get_user_by_username(username):
    url = "https://api.twitter.com/2/users/by/username/{}".format(username)
    json_response = connect_to_endpoint(url, "")
    print("User Found")
    testuid = json_response['data']['id']
    print("ID stored: " + testuid)

def create_url(id, endpoint):
    t_pre = "&tweet.fields="
    m_pre = "&expansions=attachments.media_keys&media.fields="
    
    # Adjust parameters here
    max_tweets = "100"
    tweet_fields = ""
    media_fields = "preview_image_url,type,url"
    
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs

    #url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    #url = "https://api.twitter.com/2/users/{}/tweets".format(id)
    url = ("https://api.twitter.com/2/users/{}/"+endpoint).format(id)
    params = "max_results=" + max_tweets + t_pre + tweet_fields + m_pre + media_fields

    return url, params

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2TwitterImagePython"
    return r

def connect_to_endpoint(url, tweet_fields):
    response = requests.request(
        "GET", url, auth=bearer_oauth, params=tweet_fields)
    print(response.url)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def convert_url(url):
    #?format=ext&name=orig
    ext = url[-3:]
    res = url[:-4] + '?format=' + ext + '&name=orig'
    return res

def download_image(url):
    
    file_name = url[28:43] + '.' + url[51:54]

    script_dir = os.path.dirname(__file__)
    rel_path = "downloads\\" + file_name
    path = os.path.join(script_dir, rel_path)
    
    img_data = requests.get(url).content
    print("saving " + file_name + " to " + path)
    with open(path, 'wb') as handler:
        handler.write(img_data)

def handle_json(json):
    for i in json['includes']['media']:
        media_key = i.get('media_key')
        media_type = i.get('type')
        media_url = ''
        if(media_type == 'photo'):
            media_url = i.get('url')
        elif(media_type == 'video'):
            media_url = i.get('preview_image_url')
        print(media_url)
        orig_url = convert_url(media_url)
        print(orig_url)
        download_image(orig_url)

def menu():
    print("\nTwitter Tool")
    print("1: Lookup/Store User ID")
    print("2: Download images from User's Liked tweets")
    print("3: Download images from User's tweets")
    print("4: Search Database")
    print("0: Exit")

def main():
    while(True):
        menu()
        inp = input("\nInput: ")
        if inp == '1':
            search_name = input("\nUsername: ")
            #lookup_uid(search_name)
            get_user_by_username(search_name)
        elif inp == '2':
            url, tweet_fields = create_url(testuid, "liked_tweets")
            json_response = connect_to_endpoint(url, tweet_fields)
            handle_json(json_response)
        elif inp == '3':
            url, tweet_fields = create_url(testuid, "tweets")
            json_response = connect_to_endpoint(url, tweet_fields)
            handle_json(json_response)
        elif inp == '4':
            print("To Be Implemented")
        elif inp == '0':
            break
        else:
            print("Input Valid Option")
    #json.dumps(json_response, indent=4, sort_keys=True)
    #print(json_response['includes']['media'][i]['url'])
    #f = open("myfile.txt", "w")
    #f.write(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()