from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import joblib
from datetime import datetime, timedelta
import uvicorn

# Import our models
import sys
sys.path.append('../../src')
from models.conflict_predictor import ConflictPredictor
from visualization.dashboard_generator import DashboardGenerator

app = FastAPI(title="Conflict Early Warning System API",
              description="API for predicting and analyzing conflict risks",
              version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load trained model
try:
    predictor = ConflictPredictor()
    predictor.load_model("models/trained_model.pkl")
    MODEL_LOADED = True
except:
    MODEL_LOADED = False
    print("Warning: Model not loaded. Running in demo mode.")

# Pydantic models
class TweetData(BaseModel):
    text: str
    region: Optional[str] = None
    timestamp: Optional[str] = None
    user_location: Optional[str] = None
    retweet_count: Optional[int] = 0
    favorite_count: Optional[int] = 0

class PredictionRequest(BaseModel):
    tweets: List[TweetData]
    include_visualizations: Optional[bool] = False

class PredictionResponse(BaseModel):
    predictions: List[dict]
    overall_risk: str
    high_risk_regions: List[str]
    visualization_url: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "Conflict Early Warning System API",
        "status": "active",
        "version": "1.0.0",
        "model_loaded": MODEL_LOADED
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/predict", response_model=PredictionResponse)
async def predict_conflict_risk(request: PredictionRequest):
    """
    Predict conflict risk from social media data
    """
    try:
        # Convert to DataFrame
        tweets_df = pd.DataFrame([tweet.dict() for tweet in request.tweets])
        
        # Preprocess data (simplified for demo)
        from preprocessing.text_cleaner import TextPreprocessor
        preprocessor = TextPreprocessor()
        
        # Analyze sentiment for each tweet
        predictions = []
        high_risk_count = 0
        
        for _, tweet in tweets_df.iterrows():
            analysis = preprocessor.analyze_sentiment(tweet['text'])
            
            # Add region if available
            region = tweet.get('region', 'Unknown')
            analysis['region'] = region
            
            # Determine risk level
            risk_level = analysis['risk_level']
            if risk_level in ['High', 'Critical']:
                high_risk_count += 1
            
            predictions.append(analysis)
        
        # Calculate overall risk
        total_tweets = len(predictions)
        high_risk_percentage = (high_risk_count / total_tweets * 100) if total_tweets > 0 else 0
        
        if high_risk_percentage > 70:
            overall_risk = 'Critical'
        elif high_risk_percentage > 50:
            overall_risk = 'High'
        elif high_risk_percentage > 30:
            overall_risk = 'Medium'
        else:
            overall_risk = 'Low'
        
        # Find high risk regions
        predictions_df = pd.DataFrame(predictions)
        if not predictions_df.empty and 'region' in predictions_df.columns:
            region_risks = predictions_df.groupby('region')['risk_level'].apply(
                lambda x: (x.isin(['High', 'Critical']).sum() / len(x) * 100)
            )
            high_risk_regions = region_risks[region_risks > 50].index.tolist()
        else:
            high_risk_regions = []
        
        # Generate visualization if requested
        visualization_url = None
        if request.include_visualizations and not predictions_df.empty:
            generator = DashboardGenerator()
            
            # Save visualization
            viz_data = {
                'predictions': predictions,
                'overall_risk': overall_risk,
                'high_risk_regions': high_risk_regions,
                'generated_at': datetime.now().isoformat()
            }
            
            # Save to file (in production, this would be stored in cloud storage)
            import json
            with open('visualizations/latest_prediction.json', 'w') as f:
                json.dump(viz_data, f)
            
            visualization_url = "/visualizations/latest"
        
        return PredictionResponse(
            predictions=predictions,
            overall_risk=overall_risk,
            high_risk_regions=high_risk_regions,
            visualization_url=visualization_url
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate_report/{month}/{year}")
async def generate_monthly_report(month: str, year: int):
    """
    Generate monthly conflict analysis report
    """
    try:
        # In production, this would fetch data from database
        # For demo, create sample data
        import numpy as np
        
        # Create sample data for the month
        dates = pd.date_range(start=f'{year}-{month}-01', 
                             end=f'{year}-{month}-28', freq='D')
        
        sample_data = []
        regions = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret']
        
        for date in dates:
            for region in regions:
                for _ in range(np.random.randint(5, 20)):
                    sample_data.append({
                        'date': date,
                        'region': region,
                        'vader_compound': np.random.uniform(-1, 1),
                        'conflict_intensity': np.random.uniform(0, 1),
                        'risk_level': np.random.choice(['Low', 'Medium', 'High', 'Critical'], 
                                                      p=[0.5, 0.3, 0.15, 0.05]),
                        'text': f"Sample tweet from {region} on {date.date()}"
                    })
        
        df = pd.DataFrame(sample_data)
        
        # Generate report
        generator = DashboardGenerator()
        report = generator.generate_monthly_report(df, month, year)
        
        # Generate HTML report
        html_report = generator.generate_html_report(
            report, 
            f"reports/conflict_report_{month}_{year}.html"
        )
        
        return {
            "message": "Report generated successfully",
            "report_data": report,
            "html_report_url": f"/reports/conflict_report_{month}_{year}.html",
            "download_url": f"/download/report/{month}/{year}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard")
async def get_dashboard():
    """
    Get dashboard visualization data
    """
    # In production, this would fetch real data
    # For demo, return sample dashboard data
    sample_data = {
        "heatmap_data": {
            "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "regions": ["Nairobi", "Mombasa", "Kisumu"],
            "risk_values": [[0.8, 0.6, 0.4], [0.7, 0.5, 0.3], [0.9, 0.7, 0.5]]
        },
        "map_data": [
            {"region": "Nairobi", "lat": -1.286389, "lon": 36.817223, "risk": 0.8},
            {"region": "Mombasa", "lat": -4.0435, "lon": 39.6682, "risk": 0.6},
            {"region": "Kisumu", "lat": -0.1022, "lon": 34.7617, "risk": 0.4}
        ],
        "timeline_data": {
            "dates": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "sentiment": [0.2, -0.1, -0.3],
            "intensity": [0.6, 0.7, 0.8]
        }
    }
    
    return sample_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)