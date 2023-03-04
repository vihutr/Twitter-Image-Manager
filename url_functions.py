import requests
from decouple import config

bearer_token = config('bearer_token')
# To set your environment variables in terminal run the following:
# export 'BEARER_TOKEN'='<your_bearer_token>'

def bearer_oauth(r):
    r.headers['Authorization'] = f'Bearer {bearer_token}'
    r.headers['User-Agent'] = 'v2TwitterImagePython'
    return r

def connect_to_endpoint(url, tweet_fields):
    response = requests.request(
        'GET', url, auth=bearer_oauth, params=tweet_fields)
    print(response.url)
    #print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            'Request returned an error: {} {}'.format(
                response.status_code, response.text
            )
        )
    return response.json()

def get_user_by_username(username):
    url = 'https://api.twitter.com/2/users/by/username/{}'.format(username)
    json_response = connect_to_endpoint(url, '')
    print("User Found")
    global defaultuid
    defaultuid = json_response['data']['id']
    print("User ID: " + defaultuid)
    return defaultuid

def create_url_tweets(id, max_tweets):
    tweet_fields = '&tweet.fields=attachments,author_id,context_annotations,conversation_id,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,reply_settings,source,text,withheld'
    expansions = '&expansions=attachments.poll_ids,attachments.media_keys,author_id,entities.mentions.username,geo.place_id,in_reply_to_user_id,referenced_tweets.id,referenced_tweets.id.author_id'
    media_fields = '&media.fields=duration_ms,height,media_key,preview_image_url,type,url,width,public_metrics,non_public_metrics,organic_metrics,promoted_metrics'
    user_fields = '&user.fields=created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,username,verified,withheld'
    place_fields = '&place.fields=contained_within,country,country_code,full_name,geo,id,name,place_type'
    poll_fields = '&poll.fields=duration_minutes,end_datetime,id,options,voting_status'
    # Adjust parameters here
    max_t = str(max_tweets)
    
    url = 'https://api.twitter.com/2/users/{}/tweets'.format(id)
    
    params = 'max_results=' + max_t + tweet_fields + expansions + media_fields + user_fields + place_fields + poll_fields

    return url, params

def create_url_get_tweet(ids):
    t_pre = '&tweet.fields='
    m_pre = '&expansions=attachments.media_keys&media.fields='
    
    # Adjust parameters here
    t_fields = ''
    m_fields = 'preview_image_url,type,url'
    #fields = t_pre + t_fields + m_pre + m_fields
    fields = all_fields_tweet_by_id
    url = ('https://api.twitter.com/2/tweets/')
    params = 'ids=' + ids + fields
    return url, params

def create_url(id, endpoint, max_tweets, pagination_token):
    t_pre = '&tweet.fields='
    m_pre = '&expansions=attachments.media_keys&media.fields='
    
    # Adjust parameters here
    max_t = str(max_tweets)
    t_fields = ''
    m_fields = 'preview_image_url,type,url'

    params = 'max_results=' + max_t + t_pre + t_fields + m_pre + m_fields
    
    if(pagination_token != 'N/A'):
        print("next page")
        params = params + '&pagination_token=' + pagination_token

    #url = 'https://api.twitter.com/2/users/{}/liked_tweets'.format(id)
    #url = 'https://api.twitter.com/2/users/{}/tweets'.format(id)
    url = ('https://api.twitter.com/2/users/{}/'+endpoint).format(id)

    return url, params

