import requests
import os
import sys
import json
import pandas as pd
import sqlite3
import cv2

#from TwitterAPI import TwitterAPI
from decouple import config

#Twitter API credentials using virtual environment tokens
#consumer_key = config('consumer_key')
#consumer_secret = config('consumer_secret')
#access_key = config('access_key')
#access_secret = config('access_secret')
bearer_token = config('bearer_token')

# TODO:
## Split functions to separate files; database_functions.py at minimum
## Deal with global variables; mutable dict? Classes?

script_dir = os.path.dirname(__file__)
testuid = config('test_user_id')
testusr = config('test_username')
global tweet_amount
tweet_amount = 100

# To set your environment variables in terminal run the following:
# export 'BEARER_TOKEN'='<your_bearer_token>'

def init_db():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    #cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='images'")
    cur.execute("CREATE TABLE if not exists Images (filename TEXT, localpath TEXT, id TEXT, media_key TEXT, type TEXT, tweet_url TEXT, image_url TEXT)")
    conn.commit()
    cur.close()
    conn.close()

def update_db(filename, localpath, media_key, m_type, i_url):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    update_query = '''UPDATE Images 
    SET filename = ?,
    localpath = ?,
    type = ?,
    image_url = ?
    WHERE media_key = ?'''
    data_tuple = (filename, localpath, m_type, i_url, media_key)
    cur.execute(update_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def add_to_db(filename, localpath, t_id, media_key, m_type, t_url, i_url):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    insert_query = '''INSERT INTO Images
        (filename, localpath, id, media_key, type, tweet_url, image_url) 
        VALUES (?, ?, ?, ?, ?, ?, ?);'''
    data_tuple = (filename, localpath, t_id, media_key, m_type, t_url, i_url)
    cur.execute(insert_query, data_tuple)
    conn.commit()
    cur.close()
    conn.close()

def check_media_key(media_key):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT media_key from Images where media_key=?", (media_key,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return(data)

def display_table():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    print(pd.read_sql_query("SELECT * FROM Images", conn))

def get_user_by_username(username):
    url = "https://api.twitter.com/2/users/by/username/{}".format(username)
    json_response = connect_to_endpoint(url, "")
    print("User Found")
    global testuid
    testuid = json_response['data']['id']
    print("ID stored: " + testuid)

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

    rel_path = "downloads\\" + testusr
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
    
    cv2.imshow(path, img)
    cv2.waitKey(500)
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
    for i in json['data']:
        for j in i['attachments']['media_keys']:
            media_key = j
            t_id = i.get('id')
            t_text = i.get('text')
            t_url = t_text[-23:]
            # check db if exists
            data = check_media_key(media_key)
            if not data:
                print("not found")
                add_to_db("", "", t_id, media_key, "", t_url, "")
                continue
            print("found")


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
        print(media_url)
        orig_url = convert_url(media_url)
        print(orig_url)
        file, path = download_image(orig_url)

        # update db entry
        update_db(file, path, media_key, media_type, orig_url)

def menu():
    print("-----------\n Main Menu\n-----------")
    print("1: Lookup/Store User ID")
    print("2: Download images from user's liked tweets")
    print("3: Download images from user's tweets")
    print("4: Search database")
    print("5: Change amount of tweets downloaded")
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
    init_db()
    title()
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
            display_table()
        elif inp == '5':
            tweet_amount = input("\nInput a number: ")
            print("Set new tweet amount to " + tweet_amount)
        elif inp == '9':
            url, tweet_fields = create_url(testuid, "tweets", 5)
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