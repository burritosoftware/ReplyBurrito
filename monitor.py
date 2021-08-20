import os
from dotenv import load_dotenv
import json
import time
import tweepy
from TwitterAPI import TwitterAPI # This is just here to access v2 endpoints a bit easier since tweepy doesn't fully support them yet

# Load API key and secret from .env file
load_dotenv()

# Set "tweetid" variable with TWEET_ID from .env file
tweetid = os.getenv('TWEET_ID')

# Checking for keys.json file
if os.path.exists('keys.json'):
    with open('keys.json') as f:
        keys = json.load(f)
        f.close()
        print('Keys loaded successfully!')
else: 
    print('Keys not found. Run getkeys.py to grab them!')
    quit()

# Authenticating with Twitter using keys.json for both tweepy and TwitterAPI
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
auth.set_access_token(keys['token'], keys['secret'])
api = tweepy.API(auth)
apiv2 = TwitterAPI(os.getenv('API_KEY'), os.getenv('API_SECRET'), keys['token'], keys['secret'], api_version='2')

currentuser = api.me()
print('Logged in as: ' + currentuser.screen_name)

# If text files don't exist, create them before opening
if not os.path.exists('subscribers.txt'):
    open("subscribers.txt", "w").close()
    print('Created subscribers.txt')
else:
    print('subscribers.txt found')

if not os.path.exists('blacklist.txt'):
    open("blacklist.txt", "w").close()
    print('Created blacklist.txt')
else:
    print('blacklist.txt found')

def likecheck():
    # Get likes of a tweet and output to likedusers variable
    likedresponse = apiv2.request(f'tweets/:{tweetid}/liking_users').json()
    if 'data' not in likedresponse:
        print('No likes found on tweet, skipping')
        return
    
    likedusers = likedresponse['data']

    # Open subscribers.txt and read contents into localids
    subscribersfile = open("subscribers.txt", "r+")
    localids = subscribersfile.read()
    blacklistfile = open("blacklist.txt", "r+")
    blackedids = blacklistfile.read()
    # Write each ID from likedusers to subscribers.txt if the id doesn't exist in it
    # Sends a confirmation if the ID doesn't exist
    for user in likedusers:
        if user['id'] not in localids:
            if user['id'] not in blackedids:
                subscribersfile.write(user['id'] + '\n')
                api.update_status(f'@{user["username"]} {os.getenv("MESSAGE")}')
                print(f'@{user["username"]}\'s ID added to subscriber list and confirmation sent')
        else:
            print(f'@{user["username"]} is already subscribed: skipping')
    subscribersfile.close()

def blacklistcheck():
    mentions = api.mentions_timeline(count=10)
    blacklistfile = open("blacklist.txt", "r+")
    blackedids = blacklistfile.read()

    for status in mentions:
        user = status.user
        if str(user.id) not in blackedids:
            if status.text == f'@{currentuser.screen_name} #stop':
                if status.in_reply_to_status_id is not None:
                    try:
                        parent = api.get_status(status.in_reply_to_status_id)
                        endcheck = parent.text.endswith(os.getenv("MESSAGE"))
                        if endcheck:
                            startcheck = parent.text.startswith(f'@{status.user.screen_name}')
                            if startcheck:
                                # Delete ID in subscribers.txt
                                with open("subscribers.txt", "r") as localids:
                                    idlines = localids.readlines()
                                with open("subscribers.txt", "w") as f:
                                    for id in idlines:
                                        if id.strip("\n") != str(user.id):
                                            f.write(id)
                                blacklistfile.write(str(user.id) + '\n')
                                api.update_status(f'@{user.screen_name} {os.getenv("UNSUBMESSAGE")}', status.id_str)
                                print(f'@{user.screen_name} has been blacklisted')
                    except Exception:
                        pass
    blacklistfile.close()

# Timer loop to update the subscribers list
print('Starting loop')
print('------------------')
while True:
    time.sleep(15)
    print('Checking for users who want to be blacklisted')
    blacklistcheck()
    print('Checking for new subscribers')
    likecheck()
    print('\nFinished\n------------------')