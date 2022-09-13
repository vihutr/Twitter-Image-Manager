import requests
import os
import json
#import pandas as pd

from decouple import config

# Using virtual environment tokens
bearer_token = config('bearer_token')
testuid = config('test_user_id')

# To set your environment variables in terminal run the following:
# export 'BEARER_TOKEN'='<your_bearer_token>'

t_pre = "tweet.fields="
m_pre = "&expansions=attachments.media_keys&media.fields="

def create_url(id):
    tweet_fields = t_pre + ""
    media_fields = m_pre + "preview_image_url,type,url"
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs
    url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    return url, tweet_fields+media_fields

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2LikedTweetsPython"
    return r

def connect_to_endpoint(url, tweet_fields):
    response = requests.request(
        "GET", url, auth=bearer_oauth, params=tweet_fields)
    print(response.url)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

def convert_url(url):
    ext = url[-3:]
    res = url[:-4] + '?format=' + ext + '&name=orig'
    return res

def download_image(url):
    
    file_name = url[28:43] + '.' + url[51:54]

    script_dir = os.path.dirname(__file__)
    rel_path = "downloads/" + file_name
    path = os.path.join(script_dir, rel_path)
    
    img_data = requests.get(url).content
    print("saving " + file_name + " to " + path)
    with open(path, 'wb') as handler:
        handler.write(img_data)


def main():
    #inp = input('STATEMENT')
    url, tweet_fields = create_url(testuid)
    json_response = connect_to_endpoint(url, tweet_fields)
    #json.dumps(json_response, indent=4, sort_keys=True)
    #print(json_response['includes']['media'][i]['url'])
    for i in json_response['includes']['media']:
        media_key = i.get('media_key')
        media_type = i.get('type')
        media_url = ''
        if(media_type == 'photo'):
            media_url = i.get('url')
        elif(media_type == 'video'):
            media_url = i.get('preview_image_url')
        orig_url = convert_url(media_url)

        print(orig_url)
        download_image(orig_url)
        #?format=jpg&name=orig

    #f = open("myfile.txt", "w")
    #f.write(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()