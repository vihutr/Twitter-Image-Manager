# Twitter-Image-Manager

Python script that uses Twitter API v2 endpoint (through requests) and [youtube-dl](https://github.com/ytdl-org/youtube-dl) to download media given on a twitter account's likes and tweets (retweets).

freeze to Requirements/install from respectively
## Windows:
`py -m pip freeze > Requirements.txt
py -m pip install -r Requirements.txt`

## Unix: 
`python -m pip freeze > Requirements.txt
python -m pip install -r Requirements.txt`

## Basic Use:
This script currently pulls default values from the environment variables. Add default user id and username to .env file like so:
`default_user_id = "###################"
default_username = "@username(withoutthe@)`

Files will be organized downloads/username/unsorted by default. Turning sorting will instead show each image as it is downloaded, which will be closed once a key is pressed or the windows is closed. The script will the prompt the you to enter the name of the folder to put move the image to, which can be nonexistant or already exist. This will obviously take a large amount of time the first time running on a relatively active account, and so is off by default. An option to enable sorting unsorted files later on and/or use AI to automatically tag images may be added later on.
