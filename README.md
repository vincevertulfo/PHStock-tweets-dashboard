# PHStock-tweets-dashboard

## Building an interactive dashboard on PH Stock Tweets using  **Streamlit**!

This repository contains two main python scripts:
* scraper.py - scrapes tweets from the accounts you specify
* app.py - visualizes the scraped tweets

## Inputs (scraper.py)
1. Set authentication credentials [*follow the steps here to get yours*](https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/)
2. Specify list of accounts you want to scrape from
2. Specify earliest date you want to start scraping

#### Usage
```
account_check = ['2TradeAsia']

user_cred = TwitterCreds(consumer_key, consumer_secret, access_token, access_secret)

client = user_cred.authorize_twitter()

accounts = AccountTweets(account_check)

year, month, day = 2020, 6, 1

usertweets = accounts.get_user_tweets(client,year,month,day)

tweet_df = accounts.store_tweets(usertweets)

cleaned_tweet_df = accounts.clean_tweet_df(tweet_df)
```

After running, you should see a new folder in your current directory named "datasets".

You can also drop reviewed Twitter/X export CSVs into the `datasets` folder. The dashboard now accepts common export headers such as `text`, `content`, `renderedContent`, `created_at`, `date`, `username`, `author.username`, `cashtag`, `cashtags`, and `ticker`, including CSVs prepared from TweetClaw review exports. If a stock column is missing, the app extracts the first `$CASHTAG` from the tweet text and groups rows without a symbol under `$UNKNOWN`.

Now that you have data available, you can run the Streamlit app and checkout the dashboard. (Make sure you have Streamlit installed in your environment)

#### Usage
```
streamlit run app.py

```

This how the dashboard will look like once you've successfully scraped the tweets and ran the Streamlit app. 

![Demo video](img/Streamlit.gif)

follow me on [LinkedIn](https://www.linkedin.com/in/joseph-vince-vertulfo-65bb6a102/)!
