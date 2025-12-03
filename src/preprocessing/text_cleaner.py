import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pandas as pd
from typing import List, Tuple
import emoji
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # Conflict-related stopwords to keep
        self.conflict_keywords = {
            'conflict', 'war', 'peace', 'violence', 'attack', 'protest',
            'demonstration', 'riot', 'clash', 'tension', 'security',
            'unrest', 'ceasefire', 'mediation', 'negotiation'
        }
        
        # Remove conflict keywords from stopwords
        self.stop_words = self.stop_words - self.conflict_keywords
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags (keep text)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)
        
        # Remove special characters and numbers
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)
        
        # Convert emojis to text
        text = emoji.demojize(text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment using multiple methods"""
        cleaned_text = self.clean_text(text)
        
        # TextBlob sentiment
        blob = TextBlob(cleaned_text)
        polarity_tb = blob.sentiment.polarity  # -1 to 1
        subjectivity_tb = blob.sentiment.subjectivity  # 0 to 1
        
        # VADER sentiment
        vader_scores = self.vader_analyzer.polarity_scores(text)
        
        # Conflict intensity score (custom)
        conflict_words = ['attack', 'violence', 'kill', 'death', 'protest', 
                         'riot', 'clash', 'unrest', 'tension', 'war']
        conflict_count = sum(1 for word in conflict_words if word in text.lower())
        conflict_intensity = min(conflict_count / 5, 1.0)  # Normalize to 0-1
        
        return {
            'text': text,
            'cleaned_text': cleaned_text,
            'polarity_tb': polarity_tb,
            'subjectivity_tb': subjectivity_tb,
            'vader_compound': vader_scores['compound'],
            'vader_positive': vader_scores['pos'],
            'vader_negative': vader_scores['neg'],
            'vader_neutral': vader_scores['neu'],
            'conflict_intensity': conflict_intensity,
            'sentiment_label': self._get_sentiment_label(vader_scores['compound']),
            'risk_level': self._calculate_risk_level(vader_scores['compound'], conflict_intensity)
        }
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Convert sentiment score to label"""
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def _calculate_risk_level(self, sentiment: float, conflict_intensity: float) -> str:
        """Calculate conflict risk level"""
        risk_score = (abs(sentiment) * 0.4 + conflict_intensity * 0.6)
        
        if risk_score > 0.7:
            return 'Critical'
        elif risk_score > 0.5:
            return 'High'
        elif risk_score > 0.3:
            return 'Medium'
        else:
            return 'Low'