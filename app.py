import streamlit as st
from streamlit import caching
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import datetime
from datetime import date
import glob
import os
from os import path
import fastquant as fq 
from fastquant import get_stock_data


TEXT_COLUMNS = ["cleaned_tweet", "tweet", "text", "content", "renderedContent", "full_text"]
DATE_COLUMNS = ["tweet_created_at", "created_at", "createdAt", "date", "timestamp"]
USER_COLUMNS = ["username", "screen_name", "author.username", "user.username", "handle"]
STOCK_COLUMNS = ["stock_code", "cashtag", "cashtags", "symbol", "ticker"]


def _first_existing_column(df, candidates):
  for column in candidates:
    if column in df.columns:
      return column
  return None


def _first_stock_symbol(value):
  if pd.isna(value):
    return "$UNKNOWN"
  if isinstance(value, str):
    for token in value.replace(",", " ").split():
      if token.startswith("$") and len(token) > 1:
        return token.upper()
    stripped = value.strip()
    if stripped:
      return stripped.upper() if stripped.startswith("$") else f"${stripped.upper()}"
  return "$UNKNOWN"


def _normalize_tweet_export(df):
  normalized = df.copy()

  text_column = _first_existing_column(normalized, TEXT_COLUMNS)
  if text_column and "cleaned_tweet" not in normalized.columns:
    normalized["cleaned_tweet"] = normalized[text_column].fillna("").astype(str)

  date_column = _first_existing_column(normalized, DATE_COLUMNS)
  if date_column and "tweet_created_at" not in normalized.columns:
    normalized["tweet_created_at"] = normalized[date_column]

  user_column = _first_existing_column(normalized, USER_COLUMNS)
  if user_column and "username" not in normalized.columns:
    normalized["username"] = normalized[user_column].fillna("unknown").astype(str).str.lstrip("@")

  stock_column = _first_existing_column(normalized, STOCK_COLUMNS)
  if stock_column and "stock_code" not in normalized.columns:
    normalized["stock_code"] = normalized[stock_column].apply(_first_stock_symbol)

  if "stock_code" not in normalized.columns and text_column:
    normalized["stock_code"] = normalized[text_column].apply(_first_stock_symbol)

  return normalized


st.markdown(f"<h1 style='color: black;'> Stock Tweets Dashboard! </h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: black; font-size: large'>This dashboard visualizes recent news about stocks from various twitter accounts. </p>", unsafe_allow_html=True)


st.sidebar.title("Filters")
st.sidebar.markdown("Use these filters to explore the data!")

# NOTE: Check if directory contains datasets

if not os.path.isdir('datasets') or len(glob.glob('datasets/*.csv')) == 0:

  st.markdown("No datasets available")

else:

  @st.cache(persist=True)
  def load_data():
    datasets = [_normalize_tweet_export(pd.read_csv(csv_path)) for csv_path in glob.glob('datasets/*.csv')]
    df = pd.concat(datasets, ignore_index=True)
    df['tweet_created_at'] = pd.to_datetime(df['tweet_created_at'])
    return df


  data = load_data()

  # Counter
  st.markdown(f"<h1 style='color: green; font-size: large'>{len(data)} tweets scraped from {data['username'].nunique()} account/s! </h1>", unsafe_allow_html=True)

  # Divider
  st.markdown(f"<hr>", unsafe_allow_html=True)

  # ====================Sidebar Elements================================

  st.sidebar.subheader("Choose Stock Code")
  random_stock = st.sidebar.selectbox("Stock Code", sorted(data['stock_code'].unique()))

  st.sidebar.subheader("Which dates do you want to check from?")
  start_date = st.sidebar.date_input("Start date", min(data.loc[data['stock_code'] == random_stock, 'tweet_created_at'].dt.date), key='1')
  end_date = st.sidebar.date_input("End date", max(data.loc[data['stock_code'] == random_stock, 'tweet_created_at'].dt.date), key='2')

  st.sidebar.subheader("Choose Twitter Account")
  select = st.sidebar.selectbox('Visualization type', sorted(data['username'].unique()), key=1)

  # ====================Body Elements================================


  # NOTE: Returns random tweet
  st.markdown(f"<h2 style='color: black;'> Latest Tweet for <span style='font-weight: bold;'> {random_stock} </span> ( {end_date}) </h2>", unsafe_allow_html=True)
  if start_date == end_date:  
    if(len(data.query('stock_code == @random_stock and tweet_created_at.dt.date == @start_date')[["cleaned_tweet"]]) > 0):
      st.markdown(data.query('stock_code == @random_stock and tweet_created_at.dt.date == @start_date')[["cleaned_tweet"]].sample(n=1).iat[0,0])
    else:
      st.markdown(f"No tweet for {random_stock} on {start_date}")
  elif start_date > end_date:
    st.markdown("Please input valid date range. (Start date should be earlier than end date!")
  elif start_date < end_date:
    if(len(data.query('stock_code == @random_stock and tweet_created_at.dt.date >= @start_date and tweet_created_at.dt.date <= @end_date')[["cleaned_tweet"]]) > 0):
      st.markdown(data.query("stock_code == @random_stock and tweet_created_at.dt.date == @end_date")[["cleaned_tweet"]].sample(n=1).iat[0,0])
    else:
      st.markdown(f"No tweet for {random_stock} between {start_date} and {end_date}")

  # Divider
  st.markdown(f"<hr>", unsafe_allow_html=True)


  # NOTE: Loading Stock Price data from fastquant
  st.markdown(f"<h2 style='color: black;'> Stock Price Action for <span style='font-weight: bold;'> {random_stock} </span></h2>", unsafe_allow_html=True)
  stock_fq = random_stock.lstrip('$')
  stock_df = get_stock_data(stock_fq, start_date - datetime.timedelta(days=7), date.today())
  # stock_df = stock_df.join
  fig1 = px.line(stock_df, x="dt", y="close")
  st.plotly_chart(fig1)

  
  # NOTE: DataFrame of Raw Data
  st.markdown(f"<h2 style='color: black;'> <span style='font-weight: bold;'> {random_stock} </span> Tweets based on date range </h2>", unsafe_allow_html=True)
  modified_data = data.loc[(data['tweet_created_at'].dt.date >= start_date) & (data['tweet_created_at'].dt.date <= end_date) & (data['stock_code'] == random_stock), ['username', 'tweet_created_at', 'cleaned_tweet']]
  st.markdown(f"{len(modified_data)} tweet/s between {start_date} and {end_date}")
  st.dataframe(modified_data)

  # Divider
  st.markdown(f"<hr>", unsafe_allow_html=True)

  st.markdown(f"<h2 style='color: black;'> Word Cloud for <span style='font-weight: bold;'> {random_stock} </span> </h2>", unsafe_allow_html=True)
  df = data[data['stock_code'] == random_stock]
  words = ' '.join(df['cleaned_tweet'])
  processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
  wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=640).generate(processed_words)
  plt.imshow(wordcloud)
  plt.xticks([])
  plt.yticks([])
  st.pyplot()


  # Divider
  st.markdown(f"<hr>", unsafe_allow_html=True)

  stock_count = data.loc[data['stock_code'] != '$PSEI']['stock_code'].value_counts().head(10)
  stock_count = pd.DataFrame(
    {
      'Stock': stock_count.index,
      'Tweet Count': stock_count.values
    }
  )
  st.markdown(f"<h2 style='color: black;'> Top 10 Stocks By Tweet Count </h2>", unsafe_allow_html=True)
  st.markdown(f"<p style='color: black; font-style: italic;'> Data from {min(data['tweet_created_at'].dt.date)} to {max(data['tweet_created_at'].dt.date)} </p2>", unsafe_allow_html=True)
  
  fig = px.bar(stock_count, x='Stock', y='Tweet Count',height=500)
  st.plotly_chart(fig)
