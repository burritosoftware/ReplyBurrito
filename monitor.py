import os
from dotenv import load_dotenv
import json
import time
import signal
import sys
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

def run_program():
    # Timer loop to update the subscribers list
    print(f'Starting first loop in {os.getenv("INTERVAL")} seconds, press CTRL+C to cancel')
    print('------------------')
    while True:
        time.sleep(int(os.getenv("INTERVAL")))
        print('Checking for users who want to be blacklisted')
        blacklistcheck()
        print('\nChecking for new subscribers')
        likecheck()
        print(f'\nFinished loop: next starts in {os.getenv("INTERVAL")} seconds, press CTRL+C to cancel\n------------------')

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nStop monitoring? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Tweet monitoring stopped.")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

if __name__ == '__main__':
    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    run_program()