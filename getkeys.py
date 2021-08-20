import os
from dotenv import load_dotenv
import json
import tweepy

# Load API key and secret from .env file
load_dotenv()

# Setup Tweepy OAuthHandler
auth = tweepy.OAuthHandler(os.getenv('API_KEY'), os.getenv('API_SECRET'))

# Get authorization URL and print it
try:
    redirect_url = auth.get_authorization_url()
except tweepy.TweepError:
    print('Error! Failed to get request token.')

print('Here\'s your auth URL. Open it up and give me the pin so I can grab keys!')
print(redirect_url)

# Ask for verification PIN from user
authtoken = auth.request_token['oauth_token']
verifier = input('PIN: ')

try:
    auth.get_access_token(verifier)
    api = tweepy.API(auth)
    currentuser = api.me()
    print('Logged in as: ' + currentuser.screen_name)
except tweepy.TweepError:
    print('Error! Failed to get access token.')

# Dump access token and secret to keys.json
credentials = {"token":auth.access_token, "secret":auth.access_token_secret}
keysfile = open("keys.json", "w")
keysfile.write(json.dumps(credentials))

print('Keys dumped successfully! You\'re now ready to run whatever else you want.')