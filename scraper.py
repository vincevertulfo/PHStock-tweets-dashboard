from tweepy import OAuthHandler
from tweepy import API
from tweepy import Cursor

from datetime import datetime, date, timedelta
import tweepy
import os
import pandas as pd
import glob

# TO access .env variables
from decouple import config


class TwitterCreds:
  """
    A class used to represent the user's Twitter Credentials

    ...

    Attributes
    ----------
    account_list : list
        list containing the accounts you want to scrape tweets from
    num_of_account : int
        number of accounts stored in account_list
    usertweets : list
        list storing the raw user tweets 

    Methods
    -------
    authorize_twitter(client)
        Shows list of users/accounts you want to scrape and information of each account
    """

  def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
    self.consumer_key = consumer_key
    self.consumer_secret = consumer_secret
    self.access_token = access_token
    self.access_secret = access_secret

  def authorize_twitter(self):
    auth = OAuthHandler(self.consumer_key, self.consumer_secret)
    auth.set_access_token(self.access_token, self.access_secret)
    self.client = API(auth)
    return self.client

  def __str__(self):
    return 'Client successfully created!'

class AccountTweets:
  """
    A class used to represent Tweets from various accounts

    ...

    Attributes
    ----------
    account_list : list
        list containing the accounts you want to scrape tweets from
    num_of_account : int
        number of accounts stored in account_list
    usertweets : list
        list storing the raw user tweets 
    account_names : list
        list containing the accounts you want to scrape tweets from

    Methods
    -------
    show_account_list(client)
        Shows list of users/accounts you want to scrape and information of each account
    get_user_tweets(client)
        Remove unnecessary text from the tweet 
    store_tweets(tweets)
        Stores the raw user tweets in a DataFrame
    clean_tweet_df(tweet_df)
        Cleans the raw user tweets dataframe
  """

  account_list = []
  num_of_account = 0
  usertweets = []
  
  stock_list = ['$2GO', '$AAA', '$AB', '$ABA', '$ABG', '$ABS', '$ABSP', '$AC']

  def __init__(self, account_names=None):
    self.account_name = account_names

    self.account_list.extend(account_names)

    AccountTweets.num_of_account += len(account_names)

  def show_account_list(self, client):
    """  Shows list of users/accounts you want to scrape and information of each account

    Parameters
    ----------
    client : object
        Authorized twitter API client

    Returns
    -------
    print : 
         Printing the details of each account/user
    """
    if len(self.account_list) > 0:

      for acc in self.account_list:
        print(acc)
        account = client.get_user(acc)
        num_of_tweets = account.statuses_count
        account_creation_date = account.created_at

        print("Getting tweets from " + acc)
        print("Account name " + account.name)
        print("Tweet count " + str(account.statuses_count))
        print("==========================")
    else:
      return "Account list is empty!"

  def get_user_tweets(self, client, year, month, day):
    """  Remove unnecessary text from the tweet 

    Parameters
    ----------
    client : object
        Authorized twitter API client
    since_date

    Returns
    -------
    usertweets : list
         List containing the scraped tweets
    """

    since_date = date(year,month,day)

    for acc in self.account_list:

      # NOTE: This is to make initial request for most recent tweets. Caveat: 200 is the maximum allowed count
      new_tweets = client.user_timeline(screen_name = acc, count = 200, tweet_mode='extended')

      # NOTE: Only store tweets within the specified date range
      new_tweets = [tweet for tweet in new_tweets if datetime.strptime(str(tweet.created_at), "%Y-%m-%d %H:%M:%S").date() > since_date]

      if(len(new_tweets) > 0):

        # NOTE: Store most recent tweets
        self.usertweets.extend(new_tweets)

        # NOTE: Save the ID of the oldest tweet less one
        oldest_tweet = self.usertweets[-1].id - 1

        # NOTE: Keep grabbing tweets until there are no tweets left to grab
        while len(new_tweets) > 0:
          print(f"Getting tweets before {oldest_tweet}")

          # NOTE: All subsequent requests use the max_id param to prevent duplicates
          new_tweets = client.user_timeline(screen_name = acc, count = 200, tweet_mode = 'extended', max_id = oldest_tweet)

          # NOTE: Only store tweets within the specified date range
          new_tweets = [tweet for tweet in new_tweets if datetime.strptime(str(tweet.created_at), "%Y-%m-%d %H:%M:%S").date() >= since_date]

          # NOTE: Save most recent tweets
          self.usertweets.extend(new_tweets)

          # NOTE: Update the id of the oldest tweet less one
          oldest_tweet = self.usertweets[-1].id - 1

          print(f"Downloaded {len(self.usertweets)} tweets so far!")

      else:
        print('No new tweets!')

    return self.usertweets

  def store_tweets(self, tweets):
    """  Stores the raw user tweets in a DataFrame

    Parameters
    ----------
    tweets : list
        List containing the scraped tweets

    Returns
    -------
    tweet_df : DataFrame
        DataFrame storing the raw user tweets
    """

    if(len(tweets) > 0):

      username = [tweet.user.screen_name for tweet in tweets]
      location = [tweet.user.location for tweet in tweets]
      tweet_created_at = [tweet.created_at for tweet in tweets]
      tweet = [tweet.full_text for tweet in tweets]
      hashtags = [tweet.entities['hashtags'] for tweet in tweets]


      tweet_df = pd.DataFrame([])
      tweet_df['username'] = username
      tweet_df['location'] = location
      tweet_df['tweet_created_at'] = tweet_created_at
      tweet_df['tweet'] = tweet
      tweet_df['hashtags'] = hashtags

      return tweet_df



  def clean_tweet_df(self, tweet_df):
    """  Cleans the raw user tweets dataframe

    Parameters
    ----------
    tweet_df : DataFrame
         DataFrame containing the raw user tweets

    Returns
    -------
    tweet_df : DataFrame
        New DataFrame containing the additional columns ['cleaned_tweet', 'stock code']
    """

    if os.path.exists("datasets"):
      pass
    else:
      os.makedirs('datasets')

    if tweet_df:
      tweet_df['cleaned_tweet'] = tweet_df['tweet'].apply(lambda x: self.clean_tweet(x))
      tweet_df['stock_code'] = tweet_df['tweet'].apply(lambda x: self.get_stock_code(x))

      curr_path = os.path.dirname(os.path.abspath(__file__))

      tweet_df.to_csv(os.path.join(curr_path, "datasets", f"tweets_scraped_last_{str(date.today())}.csv"), index=False, encoding='utf-8-sig')

    return tweet_df
      

  @staticmethod
  def clean_tweet(tweet_text):
    """  Remove unnecessary text from the tweet 

    Parameters
    ----------
    tweet_text : str
        Each tweet string from a text column in a DataFrame

    Returns
    -------
    new_tweet_string : str
        The cleaned tweet
    """

    split_tweet = [x for x in tweet_text.split() if 'http' not in x]

    new_tweet_string = ' '.join([word for word in split_tweet])

    return new_tweet_string
  
  @staticmethod
  def get_stock_code(tweet_text):
    """  Extracts the stock code that the tweet is referring to

    Parameters
    ----------
    tweet_text : str
        Each tweet string from a text column in a DataFrame

    Returns
    -------
    stock_code : str
       "General PSEi Updates" if tweet doesn't contain any stock code or if it contains more than one
        Specific Stock Code if tweet contains only one stock code
    """
    stock_code_df = pd.read_csv('Stock Codes.csv')
    stock_codes = set(stock_code_df['Stock Codes'].unique())

    if "$" in tweet_text:
      all_stock_codes = [x for x in tweet_text.split() if '$' in x]

      if((len(all_stock_codes) == 1) & (all_stock_codes[0] in stock_codes)):
        return all_stock_codes[0]

      else:
        return ('$PSEI')

    else:
      return ('$PSEI')


if __name__ == "__main__":

  consumer_key = config('consumer_key')
  consumer_secret = config('consumer_secret')
  access_token = config('access_token')
  access_secret = config('access_secret')


  account_check = ['2TradeAsia']

  account_list = config('account_list')

  user_cred = TwitterCreds(consumer_key, consumer_secret, access_token, access_secret)

  client = user_cred.authorize_twitter()

  accounts = AccountTweets(account_check)

  year, month, day = 2020, 6, 1

  # Check if datasets path exists and if it contains datasets

  if os.path.exists('datasets'):
    if((len(os.listdir('datasets')) > 0)):
      df = pd.concat(map(pd.read_csv, glob.glob('datasets/*.csv')))
      df['tweet_created_at'] = pd.to_datetime(df['tweet_created_at'])
      max_date = max(df['tweet_created_at'].dt.date)
      year, month, day = max_date.year, max_date.month, max_date.day
  else:
    year, month, day = year, month, day

  usertweets = accounts.get_user_tweets(client,year,month,day)

  tweet_df = accounts.store_tweets(usertweets)

  cleaned_tweet_df = accounts.clean_tweet_df(tweet_df)




