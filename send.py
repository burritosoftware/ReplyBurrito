import os
from dotenv import load_dotenv
import json
import time
import tweepy

# Load API key and secret from .env file
load_dotenv()

# Checking for keys.json file
if os.path.exists('keys.json'):
    with open('keys.json') as f:
        keys = json.load(f)
        f.close()
        print('Keys loaded successfully!')
else: 
    print('Keys not found. Run getkeys.py to grab them!')
    quit()

# If subscribers.txt doesn't exist, ask to run monitor.py
if not os.path.exists('subscribers.txt'):
    print('Looks like subscribers.txt doesn\'t exist. Run monitor.py to get subscriber IDs!')
    quit()
else:
    print('subscribers.txt found')

# Authenticating with Twitter using keys.json
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))
auth.set_access_token(keys['token'], keys['secret'])
api = tweepy.API(auth)

currentuser = api.me()
print('Logged in as: ' + currentuser.screen_name)

print('Sending Tweet(s) in 5 seconds...')
time.sleep(5)

# For every user ID in subscribers.txt, send a tweet mentioning them
with open("subscribers.txt", "r") as localids:
    idlines = localids.readlines()
    for id in idlines:
        user = api.get_user(id)
        print(f'Sending {user.screen_name}\'s Tweet')
        api.update_status(f'@{user.screen_name} {os.getenv("SENDMESSAGE")}')

print('\nFinished! Make sure to stop monitor.py and delete subscribers.txt and blacklist.txt.')