import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import xgboost as xgb
import lightgbm as lgb
import joblib
import warnings
warnings.filterwarnings('ignore')

class ConflictPredictor:
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_importance = None
        
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            ),
            'xgboost': xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='logloss'
            ),
            'lightgbm': lgb.LGBMClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=42
            )
        }
    
    def prepare_features(self, df: pd.DataFrame, target_column: str = 'conflict_risk') -> tuple:
        """Prepare features and target"""
        # Select features
        feature_columns = [
            'polarity_tb', 'vader_compound', 'conflict_intensity',
            'total_engagement', 'engagement_rate', 'dayofweek', 'hour',
            'month_sin', 'month_cos', 'hour_sin', 'hour_cos'
        ]
        
        # Add region features if they exist
        region_cols = [col for col in df.columns if col.startswith('region_')]
        feature_columns.extend(region_cols)
        
        # Add lag features if they exist
        lag_cols = [col for col in df.columns if 'lag' in col or 'rolling' in col]
        feature_columns.extend(lag_cols)
        
        # Keep only existing columns
        feature_columns = [col for col in feature_columns if col in df.columns]
        
        X = df[feature_columns]
        y = df[target_column]
        
        return X, y, feature_columns
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series):
        """Train the model"""
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Get model
        self.model = self.models[self.model_type]
        
        # Hyperparameter tuning
        if self.model_type == 'random_forest':
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5, 10]
            }
            grid_search = GridSearchCV(self.model, param_grid, cv=5, scoring='accuracy')
            grid_search.fit(X_train_scaled, y_train)
            self.model = grid_search.best_estimator_
            print(f"Best parameters: {grid_search.best_params_}")
        else:
            self.model.fit(X_train_scaled, y_train)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X_train.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions"""
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        return predictions, probabilities
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series):
        """Evaluate model performance"""
        predictions, probabilities = self.predict(X_test)
        
        accuracy = accuracy_score(y_test, predictions)
        print(f"Accuracy: {accuracy:.2%}")
        print("\nClassification Report:")
        print(classification_report(y_test, predictions))
        
        # Confusion matrix
        cm = confusion_matrix(y_test, predictions)
        print("\nConfusion Matrix:")
        print(cm)
        
        return {
            'accuracy': accuracy,
            'predictions': predictions,
            'probabilities': probabilities,
            'confusion_matrix': cm
        }
    
    def save_model(self, filepath: str):
        """Save model to disk"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_importance': self.feature_importance
        }, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from disk"""
        saved_data = joblib.load(filepath)
        self.model = saved_data['model']
        self.scaler = saved_data['scaler']
        self.feature_importance = saved_data['feature_importance']
        print(f"Model loaded from {filepath}")