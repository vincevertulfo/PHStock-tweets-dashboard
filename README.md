# PHStock-tweets-dashboard

## Building an interactive dashboard on PH Stock Tweets using  **Streamlit**!

This repository contains two main python scripts:
* scraper.py - scrapes tweets from the accounts you specify
* app.py - visualizes the scraped tweets

## Inputs (scraper.py)
1. Set authentication credentials [*follow the steps here to get yours*](https://www.slickremix.com/docs/how-to-get-api-keys-and-tokens-for-twitter/)
2. Specify list of accounts you want to scrape from
2. Specify earliest date you want to start scraping

#### Sample Usage
```
user_cred = TwitterCreds(consumer_key, consumer_secret, access_token, access_secret)

client = user_cred.authorize_twitter()

accounts = AccountTweets(account_check)

```


follow me on [LinkedIn](https://www.linkedin.com/in/joseph-vince-vertulfo-65bb6a102/)!