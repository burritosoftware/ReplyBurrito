# ReplyBurrito
A free alternative to Arrow/QWVR using a mix of the Twitter 1.1 and 2.0 APIs.

## Quick Setup

### Requirements
- **Python 3**

1. Clone the source to your computer.
```
git clone https://github.com/burritosoftware/ReplyBurrito.git
cd ReplyBurrito
```

2. Install all required dependencies.
```
pip install -r requirements.txt
```

3. Make a copy of `.env.example` and name it `.env`, then fill it out with an app key and secret from the Twitter Developer Portal. **Make sure the app has read and write permissions.**

4. Run `getkeys.py`. Open the URL, authenticate with the Twitter account you want to use, and then paste the PIN back into the console so the script can save your keys to `keys.json`. **Don't share this file with anyone!**

5. Fill out the messages you want to send in `.env`, as well as change the interval if you don't want the default of 13. You should also send your Tweet you want to monitor, copy the ID from the URL, and put it in here.

6. Run `monitor.py` to begin monitoring the tweet.

7. When you're ready to send your scheduled tweet, stop `monitor.py` and run `send.py` to send tweets to each subscriber.