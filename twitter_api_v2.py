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
    defaultuid = json_response['data']['id']
    print("ID stored: " + defaultuid)
    return defaultuid


