import requests
import os
import sys
import json
import pandas as pd
import sqlite3
import cv2
import database_functions as dbf

#from TwitterAPI import TwitterAPI
from decouple import config

#Twitter API credentials using virtual environment tokens
#consumer_key = config('consumer_key')
#consumer_secret = config('consumer_secret')
#access_key = config('access_key')
#access_secret = config('access_secret')
bearer_token = config('bearer_token')

# TODO:
## List of potential error handlings:
### attachment - extended tweets do not include proper fields
### liked tweets that are quote tweets
## -> Account for extended tweets as RTs; investigate other "edge" cases
## Split functions to separate files
## single connection for database? how to split into functions then?
## Deal with global variables; mutable dict? Classes?
## Database search/display as file structure;
## how to update database when manipulating files through file manager

script_dir = os.path.dirname(__file__)
testuid = config('test_user_id')
testusr = config('test_username')
all_fields_tweet_by_id = "&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,edit_controls,edit_history_tweet_ids,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&expansions=attachments.media_keys,attachments.poll_ids,author_id,edit_history_tweet_ids,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&media.fields=alt_text,duration_ms,height,media_key,preview_image_url,public_metrics,type,url,variants,width&poll.fields=duration_minutes,end_datetime,id,options,voting_status&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type"

# To set your environment variables in terminal run the following:
# export 'BEARER_TOKEN'='<your_bearer_token>'

def get_user_by_username(username):
    url = "https://api.twitter.com/2/users/by/username/{}".format(username)
    json_response = connect_to_endpoint(url, "")
    print("User Found")
    global testuid
    testuid = json_response['data']['id']
    print("ID stored: " + testuid)

def create_url_tweets(id, max_tweets):
    tweet_fields = "&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld"
    expansions = "&expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id"
    media_fields = "&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics"
    user_fields = "&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld"
    place_fields = "&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type"
    poll_fields = "&poll.fields=duration_minutes,end_datetime,id,options,voting_status"
    # Adjust parameters here
    max_t = str(max_tweets)
    
    url = "https://api.twitter.com/2/users/{}/tweets".format(id)
    #url = ("https://api.twitter.com/2/users/{}/tweets?expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type&poll.fields=duration_minutes,end_datetime,id,options,voting_status&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics".format(id)
    
    #params = "expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type&poll.fields=duration_minutes,end_datetime,id,options,voting_status&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics"

    params = "max_results=" + max_t + tweet_fields + expansions + media_fields + user_fields + place_fields + poll_fields

    return url, params

def create_url_get_tweet(ids):
    t_pre = "&tweet.fields="
    m_pre = "&expansions=attachments.media_keys&media.fields="
    
    # Adjust parameters here
    t_fields = ""
    m_fields = "preview_image_url,type,url"
    #fields = t_pre + t_fields + m_pre + m_fields
    fields = all_fields_tweet_by_id
    url = ("https://api.twitter.com/2/tweets/")
    params = "ids=" + ids + fields
    return url, params


def create_url(id, endpoint, max_tweets):
    t_pre = "&tweet.fields="
    m_pre = "&expansions=attachments.media_keys&media.fields="
    
    # Adjust parameters here
    max_t = str(max_tweets)
    t_fields = ""
    m_fields = "preview_image_url,type,url"
    
    # You can adjust ids to include a single Tweets.
    # Or you can add to up to 100 comma-separated IDs

    #url = "https://api.twitter.com/2/users/{}/liked_tweets".format(id)
    #url = "https://api.twitter.com/2/users/{}/tweets".format(id)
    url = ("https://api.twitter.com/2/users/{}/"+endpoint).format(id)
    params = "max_results=" + max_t + t_pre + t_fields + m_pre + m_fields

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

def check_dir(path):
    if os.path.exists(path) == False:
        os.makedirs(path)

def download_image(url):
    
    #only for images
    file_name = url[28:43] + '.' + url[51:54]
    
    rel_path = os.path.join("downloads", testusr)
    folder_path = os.path.join(script_dir, rel_path)
    print(folder_path)
    check_dir(folder_path)

    path = os.path.join(folder_path, file_name)
    print(path)

    img_data = requests.get(url).content
    print("saving " + file_name + " to " + path)
    with open(path, 'wb') as handler:
        handler.write(img_data)
    
    img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    screen_res = 1920, 1080
    scale_width = screen_res[0] / img.shape[1]
    scale_height = screen_res[1] / img.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(img.shape[1] * scale)
    window_height = int(img.shape[0] * scale)
    cv2.namedWindow(path, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(path, window_width, window_height)
    cv2.moveWindow(path, 0,0)
    cv2.imshow(path, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    pathinput = input("Folder Name:")    
    new_folder_path = os.path.join(folder_path, pathinput) 
    check_dir(new_folder_path) 
    new_path = os.path.join(new_folder_path, file_name)
    if(not os.path.exists(new_path)):
        print("moving " + path + " to " + new_path)
        os.rename(path, new_path)
    else:
        print("file already exists, skipping")
    return(file_name, new_path)

def handle_json(json):
    for i in json['includes']['media']:
        media_key = i.get('media_key')
        media_type = i.get('type')
        media_url = ''
        
        print(media_type)
        if(media_type == 'photo'):
            media_url = i.get('url')
        elif((media_type == 'video') or (media_type == 'animated_gif')):
            #media_url = i.get('preview_image_url')
            #ignore video/animated gif for now
            continue

        check_mkey = dbf.check_media_key(media_key)
        if check_mkey:
            print("found")
            continue
        print("not found")

        print(media_url)
        orig_url = convert_url(media_url)
        print(orig_url)
        file, path = download_image(orig_url)

        # update db entry
        dbf.add_to_db(file, path, "", media_key, media_type, "", orig_url)
        
    
    for i in json['data']:
        print(i)
        #if()
        try:
            print(i['attachments']['media_keys'])
        except KeyError:
            print("No media key")
            #add dump for tweets with keyerror
        else:
            for j in i['attachments']['media_keys']:
                media_key = j
                t_id = i.get('id')
                t_text = i.get('text')
                t_url = t_text[-23:]
                # check db if exists
                dbf.update_db(t_id, t_url, media_key)

        

def menu():
    print("-----------\n Main Menu\n-----------")
    print("1: Lookup/Store User ID")
    print("2: Download images from user's liked tweets")
    print("3: Download images from user's tweets")
    print("4: Search database")
    #print("5: Testing: All Fields Request - Retweets")
    print("8: Change amount of tweets downloaded")
    print("9: Sample JSON")
    print("0: Exit")

def title():
    print(
        '''
    ████████        ████████        ███    ███    
       ██              ██           ████  ████    
       ██              ██           ██ ████ ██    
       ██              ██           ██  ██  ██    
       ██    ██     ████████ ██     ██      ██ ██                                               
        '''
    )

def main():
    dbf.init_db()
    title()
    tweet_amount = 100
    while(True):
        menu()
        inp = input("\nChoose an Option: ")
        if inp == '1':
            global testusr
            testusr = input("\nInput a Username (no @): ")
            get_user_by_username(testusr)
        elif inp == '2':
            url, tweet_fields = create_url(testuid, "liked_tweets", tweet_amount)
            json_response = connect_to_endpoint(url, tweet_fields)
            handle_json(json_response)
        elif inp == '3':
            url, tweet_fields = create_url(testuid, "tweets", tweet_amount)
            json_response = connect_to_endpoint(url, tweet_fields)
            handle_json(json_response)
        elif inp == '4':
            dbf.display_table()
        elif inp == '5':
            url, tweet_fields = create_url_get_tweet('1580377326780833792')
            json_response = connect_to_endpoint(url, tweet_fields)
            f = open("dump.txt", "w")
            f.write(json.dumps(json_response, indent=4, sort_keys=True))
        elif inp == '8':
            tweet_amount = int(input("\nInput a number from 5 to 100: "))
            while(tweet_amount < 5 or tweet_amount > 100):
                print("Number not in proper range.")
                tweet_amount = int(input("\nInput a number from 5 to 100: "))
            print("Set new tweet amount to " + str(tweet_amount))
        elif inp == '9':
            url, tweet_fields = create_url_tweets(testuid, 5)
            json_response = connect_to_endpoint(url, tweet_fields)
            print(json.dumps(json_response, indent = 2))
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