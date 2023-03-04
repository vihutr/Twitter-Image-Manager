import requests
import os
import sys
import json
#import logging
#logging.basicConfig(filename='TIM.log', encoding='utf-8', level=logging.DEBUG)

import database_functions as dbf
import url_functions as urlf
import imgdl
import ytdl

#from TwitterAPI import TwitterAPI
from decouple import config

#Twitter API credentials using virtual environment tokens
#consumer_key = config('consumer_key')
#consumer_secret = config('consumer_secret')
#access_key = config('access_key')
#access_secret = config('access_secret')

# TODO:
## allow user to sort unsorted images after the fact
## allow user to specify download directory
## allow user to move files throughout directories manually and have databse automatically update path
## save newest id from meta to .env, while instanced dict holds 
## List of potential error handlings:
### attachment - extended tweets do not include proper fields
### liked tweets that are quote tweets
## -> Account for extended tweets as RTs; investigate other "edge" cases
## single connection for database? how to split into functions then?
## Deal with global variables; mutable dict? Classes?
## Database search/display as file structure;
## how to update database when manipulating files through file manager
## -> Version with UI
## Change downloading to be asynchronous

## hope twitter not only doesn't die but improves as a platform :)

# create class(es) for the following and incoporate into main function

script_dir = os.path.dirname(__file__)

all_fields_tweet_by_id = '&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,edit_controls,edit_history_tweet_ids,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld&expansions=attachments.media_keys,attachments.poll_ids,author_id,edit_history_tweet_ids,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id&media.fields=alt_text,duration_ms,height,media_key,preview_image_url,public_metrics,type,url,variants,width&poll.fields=duration_minutes,end_datetime,id,options,voting_status&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type'

LIKE = 'like'
TWEET  = 'tweet'

class Instance:
    def __init__(self, user, options):
        self.user = user
        self.options = options

class Options:
    def __init__(self, sort, download_path, download_amount):
        self.sort = sort
        self.download_path = download_path
        self.download_amount = self.download_amount

class TwitterUser:
    def __init__(self, username, userid, like, tweet):
        self.username = username
        self.userid = userid
        self.like = like
        self.tweet = tweet

    def __str__(self):
        return f"Username:      {self.username}\nUser Id:       {self.userid}\nNewest Like:   {self.like}\nNewest Tweet:  {self.tweet}"

    def lookup_user(self, username):
        self.username = username
        self.userid = urlf.get_user_by_username(username) 
        newest = dbf.lookup_newest_ids(username)
        if not newest:
            dbf.add_username(self.username, self.userid, '', '')
        else:
            self.like = newest[0][0] 
            self.tweet = newest[0][1]

    def update_newest(self, type, newest):
        if type == LIKE:
            self.like = newest
        elif type == TWEET:
            self.tweet = newest

#TwitterUser = TwitterUser(defaultusr, defaultuid, newest_ids['like'], newest_ids['tweet'])

def get_orig_image_url(url):
    #?format=ext&name=orig
    url,ext = url.rsplit('.', 1)
    print(url,ext)
    result = url + '?format=' + ext + '&name=orig'
    return result
def handle_json(json, jtype, sort, CurrentUser):
    #newest_ids[likes] = config('last_liked')
    #newest_ids[tweets] = config('last_tweet')
    loopcheck = 1
    #if(!sort):
    #    sortFolder = "unsorted" 
    newestcheck = ''
    if(jtype == LIKE):
        print(LIKE)
        newestcheck = CurrentUser.like 
    elif(jtype == TWEET):
        print(TWEET)
        newestcheck = CurrentUser.tweet 
    media_count = 0
    # add dump for tweets with keyerror
    video_mkeys = {}
    download_folder = 'downloads'
    download_path = os.path.join(script_dir,download_folder)
    folder_path = os.path.join(download_path,CurrentUser.username)
    animated_path = os.path.join(download_folder,CurrentUser.username)
    if not sort:
        folder_path = os.path.join(folder_path,'unsorted')
        u_a = os.path.join('unsorted', 'animated')
        animated_path = os.path.join(animated_path, u_a)
    else:
        animated_path = os.path.join(animated_path, 'animated')
    for i in json['includes']['media']:
        media_key = i.get('media_key')
        media_type = i.get('type')
        print(media_type)
        if (dbf.check_media_key(media_key)):
            print(f"{media_key} found in database")
            continue
        print(f"{media_key} not found in database, continuing")

        media_url = ''
        print()
        if(getattr(CurrentUser, jtype) == media_key):
            loopcheck = 0
        print(f"Media Type: {media_type}")
        if(media_type == 'photo'):
            media_url = i.get('url')
            print(f"URL: {media_url}")
            media_url = get_orig_image_url(media_url)
            img_dl = imgdl.ImageDownloader(folder_path, sort)
            file, path = img_dl.download_image(media_url, CurrentUser.username)

            print(media_url)
            dbf.add_to_db(file, path, '', media_key, media_type, '', media_url)

        elif((media_type == 'video') or (media_type == 'animated_gif')):
            video_mkeys.update({media_key:media_type})
            continue
        media_count += 1
    
    for i in json['data']:
        #print(i)
        try:
            print(i['attachments']['media_keys'])
        except KeyError:
            print("No media key")
            ##add dump for tweets with keyerror
        else:
            for j in i['attachments']['media_keys']:
                media_key = j
                t_id = i.get('id')
                if t_id == newestcheck:
                    print("Newest tweet id found, ending on this loop")
                    loopcheck = 0
                t_text = i.get('text')
                t_url = t_text[-23:]

                if media_key in video_mkeys:
                    # maybe add previewing later with mpv, for now stuff into unsorted default folder
                    vid_dl = ytdl.VideoDownloader(animated_path, sort)
                    try:
                        media_url, file_name = vid_dl.download_video(t_url)
                        path = os.path.join(animated_path, file_name)
                        print('Full Info of video:')
                        print(file_name, path, t_id, media_key, video_mkeys[media_key], t_url, media_url)
                        dbf.add_to_db(file_name, path, t_id, media_key, video_mkeys[media_key], t_url, media_url)
                    except:
                        print("False Video/Video within tweet static images")
                        falsevideofilelist = open("check.txt", "a")
                        falsevideofilelist.writeline(t_url + '\n')
                        falsevideofilelist.write(media_url + '')
                        falsevideofilelist.close()

                    continue
                    # currently only dl's first video/agif given multiple in a single tweet, fix with ffmpeg and manually parsing ytdl extract info json?

                
                # check db if exists
                dbf.update_db(t_id, t_url, media_key)
    print(f"Images Downloaded: {media_count}")
    return(loopcheck)


def menu():
    print("-----------\n Main Menu\n-----------")
    print("1: Lookup/Store User ID")
    print("2: Download images from likes")
    print("3: Download images from tweets")
    print("4: Search database")
    #print("5: Testing: Get Tweet")
    print("7: Toggle Sorting On/Off (Default Off)")
    print("8: Change amount of tweets downloaded")
    #print("9: Sample JSON")
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
    title()
    dbf.init_db()
    defaultuid = config('default_user_id')
    defaultusr = config('default_username')
    most_recent_ids = dbf.lookup_newest_ids(defaultusr)
    if not most_recent_ids:
        dbf.add_username(defaultusr, defaultuid, '', '')
        most_recent_ids = [['0','0']]

    CurrentUser = TwitterUser(defaultusr, defaultuid, most_recent_ids[0][0], most_recent_ids[0][1])

    tweet_amount = 100
    sort = False

    while(True):
        print(CurrentUser)
        menu()
        inp = input("\nChoose an Option: ")
        if inp == '1':
            new_username = input("\nInput a Username (no @): ")
            CurrentUser.lookup_user(new_username)
            print(CurrentUser)

        # Fix this mess with recursion (2 and 3)
        elif inp == '2':
            url, tweet_fields = urlf.create_url(CurrentUser.userid, 'liked_tweets', tweet_amount, 'N/A')
            json_response = urlf.connect_to_endpoint(url, tweet_fields)
            newest_id = json_response['data'][0]['id']
            next_token = json_response['meta']['next_token']
            print(newest_id)
            dbf.update_newest(CurrentUser.username, LIKE, newest_id)
            CurrentUser.update_newest(LIKE, newest_id)
            f = open('jsondump.txt', 'w')
            f.write(json.dumps(json_response, indent=4, sort_keys=True))
            loop = handle_json(json_response, LIKE, sort, CurrentUser)
            pagecount = 0
            while(loop):
                print(f"Page # {pagecount}")
                #input('Press a key to continue...')
                url, tweet_fields = urlf.create_url(CurrentUser.userid, 'liked_tweets', tweet_amount, next_token)
                json_response = urlf.connect_to_endpoint(url, tweet_fields)
                next_token = json_response['meta']['next_token']
                loop = handle_json(json_response, LIKE, sort, CurrentUser)
                pagecount += 1

        elif inp == '3':
            url, tweet_fields = urlf.create_url(CurrentUser.userid, 'tweets', tweet_amount, 'N/A')
            json_response = urlf.connect_to_endpoint(url, tweet_fields)
            newest_id = json_response['meta']['newest_id']
            next_token = json_response['meta']['next_token']
            print(newest_id)
            dbf.update_newest(CurrentUser.username, TWEET, newest_id)
            CurrentUser.update_newest(TWEET, newest_id)
            f = open('jsondump.txt', 'w')
            f.write(json.dumps(json_response, indent=4, sort_keys=True))
            loop = handle_json(json_response, TWEET, sort, CurrentUser)
            pagecount = 0
            while(loop):
                print(f"Page # {pagecount}")
                #input('Press a key to continue...')
                url, tweet_fields = urlf.create_url(CurrentUser.userid, 'tweets', tweet_amount, next_token)
                json_response = urlf.connect_to_endpoint(url, tweet_fields)
                try:
                    next_token = json_response['meta']['next_token']
                except KeyError:
                    print("Last Page of Tweets Reached")
                    break

                loop = handle_json(json_response, TWEET, sort, CurrentUser)
                pagecount += 1

        elif inp == '4':
            dbf.display_table()
        #elif inp == '5':
        #    url, tweet_fields = urlf.create_url_get_tweet('1580377326780833792')
        #    json_response = urlf.connect_to_endpoint(url, tweet_fields)
        #    f = open('dump.txt', 'w')
        #    f.write(json.dumps(json_response, indent=4, sort_keys=True))
        elif inp == '7':
            sort = not sort
            print(f"Sorting = {sort}")
        elif inp == '8':
            tweet_amount = int(input("\nInput a number from 5 to 100: "))
            while(tweet_amount < 5 or tweet_amount > 100):
                print("Number not in proper range.")
                tweet_amount = int(input("\nInput a number from 5 to 100: "))
            print("Set new tweet amount to " + str(tweet_amount))
        elif inp == '9':
            url, tweet_fields = urlf.create_url_tweets(CurrentUser.userid, 5)
            json_response = urlf.connect_to_endpoint(url, tweet_fields)
            print(json.dumps(json_response, indent = 2))
        elif inp == '0':
            break
        elif inp == 'delete':
            dbf.delete_newest(CurrentUser.username)
        else:
            print("Invalid Input")
    #json.dumps(json_response, indent=4, sort_keys=True)
    #print(json_response['includes']['media'][i]['url'])
    #f = open('myfile.txt', 'w')
    #f.write(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
