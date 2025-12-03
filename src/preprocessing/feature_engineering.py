import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import holidays

class FeatureEngineer:
    def __init__(self):
        self.kenya_holidays = holidays.Ke()
    
    def create_temporal_features(self, df: pd.DataFrame, date_column: str = 'created_at') -> pd.DataFrame:
        """Create temporal features from date"""
        df = df.copy()
        
        if date_column in df.columns:
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Temporal features
            df['year'] = df[date_column].dt.year
            df['month'] = df[date_column].dt.month
            df['week'] = df[date_column].dt.isocalendar().week
            df['day'] = df[date_column].dt.day
            df['dayofweek'] = df[date_column].dt.dayofweek
            df['hour'] = df[date_column].dt.hour
            df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
            df['is_holiday'] = df[date_column].dt.date.isin(self.kenya_holidays).astype(int)
            
            # Cyclical encoding for time features
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
            df['day_sin'] = np.sin(2 * np.pi * df['day'] / 31)
            df['day_cos'] = np.cos(2 * np.pi * df['day'] / 31)
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        return df
    
    def create_engagement_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create social media engagement features"""
        df = df.copy()
        
        if 'retweet_count' in df.columns and 'favorite_count' in df.columns:
            df['total_engagement'] = df['retweet_count'] + df['favorite_count']
            df['engagement_rate'] = df['total_engagement'] / (df['total_engagement'].max() + 1)
            df['has_high_engagement'] = (df['total_engagement'] > df['total_engagement'].median()).astype(int)
        
        return df
    
    def create_geo_features(self, df: pd.DataFrame, 
                           region_coords: Dict[str, Tuple[float, float]]) -> pd.DataFrame:
        """Create geographical features"""
        df = df.copy()
        
        if 'user_location' in df.columns:
            # Simple region mapping based on location text
            df['region'] = df['user_location'].apply(
                lambda x: self._map_location_to_region(x, region_coords)
            )
            
            # One-hot encode regions
            for region in region_coords.keys():
                df[f'region_{region}'] = (df['region'] == region).astype(int)
        
        return df
    
    def _map_location_to_region(self, location: str, 
                               region_coords: Dict[str, Tuple[float, float]]) -> str:
        """Map location text to region"""
        if not isinstance(location, str):
            return 'Unknown'
        
        location_lower = location.lower()
        
        # Simple keyword-based mapping (you'd want a more sophisticated approach)
        region_keywords = {
            'Nairobi': ['nairobi', 'nrb'],
            'Mombasa': ['mombasa', 'mom', 'coast'],
            'Kisumu': ['kisumu', 'lake', 'nyanza'],
            'Nakuru': ['nakuru', 'rift'],
            'Eldoret': ['eldoret', 'uasin'],
            'Meru': ['meru', 'eastern']
        }
        
        for region, keywords in region_keywords.items():
            if any(keyword in location_lower for keyword in keywords):
                return region
        
        return 'Other'
    
    def create_lag_features(self, df: pd.DataFrame, 
                           value_column: str, 
                           group_column: str = 'region',
                           lag_periods: List[int] = [1, 7, 30]) -> pd.DataFrame:
        """Create lag features for time series"""
        df = df.copy()
        df.sort_values(['date', group_column], inplace=True)
        
        for lag in lag_periods:
            df[f'{value_column}_lag_{lag}'] = df.groupby(group_column)[value_column].shift(lag)
            df[f'{value_column}_rolling_mean_{lag}'] = df.groupby(group_column)[value_column].transform(
                lambda x: x.rolling(lag, min_periods=1).mean()
            )
        
        return df