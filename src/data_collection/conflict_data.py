import requests
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
import os

class ConflictDataCollector:
    def __init__(self):
        self.base_urls = {
            'acled': 'https://api.acleddata.com/acled/read',
            'ged': 'http://ucdpapi.pcr.uu.se/api/gedevents/'
        }
        
    def fetch_acled_data(self, country: str = 'Kenya', 
                        start_date: str = '2023-01-01',
                        end_date: str = None) -> pd.DataFrame:
        """
        Fetch data from ACLED API
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'country': country,
            'event_date': f'{start_date}|{end_date}',
            'limit': 1000
        }
        
        try:
            response = requests.get(self.base_urls['acled'], params=params)
            if response.status_code == 200:
                data = response.json()
                df = pd.DataFrame(data['data'])
                return df
        except Exception as e:
            print(f"Error fetching ACLED data: {e}")
            
        return pd.DataFrame()
    
    def create_synthetic_data(self, regions: List[str], 
                            start_date: str = '2023-01-01',
                            end_date: str = '2024-01-01') -> pd.DataFrame:
        """
        Create synthetic conflict data for demonstration
        """
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        data = []
        
        conflict_types = ['Violent Conflict', 'Protest', 'Riots', 'Battle', 'Explosion']
        severity_levels = ['Low', 'Medium', 'High', 'Critical']
        
        for date in date_range:
            for region in regions:
                # Generate random conflict events (more on certain days)
                if pd.np.random.random() < 0.3:  # 30% chance of conflict per day per region
                    num_events = pd.np.random.randint(1, 5)
                    for _ in range(num_events):
                        event = {
                            'event_date': date.strftime('%Y-%m-%d'),
                            'region': region,
                            'conflict_type': pd.np.random.choice(conflict_types),
                            'severity': pd.np.random.choice(severity_levels),
                            'fatalities': pd.np.random.randint(0, 50),
                            'latitude': pd.np.random.uniform(-4.0, 4.0),
                            'longitude': pd.np.random.uniform(33.0, 41.0),
                            'source': 'synthetic',
                            'description': f"Conflict event in {region}"
                        }
                        data.append(event)
        
        return pd.DataFrame(data)