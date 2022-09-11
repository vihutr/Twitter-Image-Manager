import requests
import os
import json
import pandas as pd

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


def main():
    #inp = input('STATEMENT')
    url, tweet_fields = create_url(testuid)
    json_response = connect_to_endpoint(url, tweet_fields)
    #json.dumps(json_response, indent=4, sort_keys=True)
    for i in json_response.items():
        print(i)
    #f = open("myfile.txt", "w")
    #f.write(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()