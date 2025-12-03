import tweepy
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import List, Dict
import os

class TwitterScraper:
    def __init__(self, consumer_key=None, consumer_secret=None, 
                 access_token=None, access_token_secret=None):
        """Initialize Twitter API client"""
        self.consumer_key = consumer_key or os.getenv('TWITTER_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('TWITTER_CONSUMER_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)
    
    def search_tweets(self, query: str, count: int = 100, 
                      geocode: str = None, lang: str = 'en') -> pd.DataFrame:
        """
        Search for tweets based on query
        
        Args:
            query: Search query (e.g., 'conflict Kenya')
            count: Number of tweets to retrieve
            geocode: "latitude,longitude,radius" (e.g., "-1.286389,36.817223,100km")
            lang: Language code
            
        Returns:
            DataFrame with tweet data
        """
        tweets_data = []
        
        try:
            tweets = tweepy.Cursor(
                self.api.search_tweets,
                q=query,
                geocode=geocode,
                lang=lang,
                tweet_mode='extended',
                count=count
            ).items(count)
            
            for tweet in tweets:
                tweet_info = {
                    'tweet_id': tweet.id_str,
                    'created_at': tweet.created_at,
                    'text': tweet.full_text,
                    'user_id': tweet.user.id_str,
                    'user_name': tweet.user.screen_name,
                    'user_location': tweet.user.location,
                    'retweet_count': tweet.retweet_count,
                    'favorite_count': tweet.favorite_count,
                    'hashtags': [hashtag['text'] for hashtag in tweet.entities['hashtags']],
                    'mentions': [mention['screen_name'] for mention in tweet.entities['user_mentions']],
                    'urls': [url['expanded_url'] for url in tweet.entities['urls']],
                    'coordinates': tweet.coordinates,
                    'place': tweet.place.full_name if tweet.place else None,
                    'language': tweet.lang,
                    'is_retweet': hasattr(tweet, 'retweeted_status')
                }
                tweets_data.append(tweet_info)
                
        except Exception as e:
            print(f"Error fetching tweets: {e}")
            
        return pd.DataFrame(tweets_data)
    
    def search_by_location(self, locations: List[Dict], 
                          keywords: List[str] = None) -> pd.DataFrame:
        """
        Search tweets from specific locations with conflict-related keywords
        
        Args:
            locations: List of dicts with 'name', 'lat', 'lon', 'radius'
            keywords: List of conflict-related keywords
            
        Returns:
            Combined DataFrame
        """
        if keywords is None:
            keywords = [
                'conflict', 'violence', 'protest', 'demonstration',
                'clash', 'tension', 'unrest', 'riot', 'attack',
                'security', 'peace', 'mediation', 'ceasefire'
            ]
        
        all_tweets = []
        
        for location in locations:
            print(f"Searching in {location['name']}...")
            geocode = f"{location['lat']},{location['lon']},{location['radius']}"
            
            for keyword in keywords:
                query = f"{keyword} -filter:retweets"
                try:
                    tweets_df = self.search_tweets(
                        query=query,
                        count=50,
                        geocode=geocode,
                        lang='en'
                    )
                    if not tweets_df.empty:
                        tweets_df['location'] = location['name']
                        tweets_df['keyword'] = keyword
                        all_tweets.append(tweets_df)
                        print(f"  Found {len(tweets_df)} tweets for '{keyword}'")
                    
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    print(f"  Error for keyword '{keyword}': {e}")
                    continue
        
        if all_tweets:
            return pd.concat(all_tweets, ignore_index=True)
        return pd.DataFrame()
    
    def save_to_csv(self, df: pd.DataFrame, filename: str):
        """Save tweets to CSV"""
        if not df.empty:
            filepath = f"data/raw/twitter/{filename}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filepath, index=False)
            print(f"Saved {len(df)} tweets to {filepath}")
            return filepath
        return None