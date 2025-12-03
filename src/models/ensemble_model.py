import numpy as np
from sklearn.ensemble import VotingClassifier
from sklearn.base import BaseEstimator, ClassifierMixin
import joblib

class ConflictEnsembleModel(BaseEstimator, ClassifierMixin):
    def __init__(self):
        self.models = {}
        self.ensemble = None
        self.classes_ = None
        
    def fit(self, X, y):
        """Train ensemble of models"""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.svm import SVC
        from sklearn.neural_network import MLPClassifier
        import xgboost as xgb
        
        # Define base models
        self.models = {
            'rf': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
            'gb': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'xgb': xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False),
            'svm': SVC(probability=True, random_state=42),
            'mlp': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
        }
        
        # Create voting classifier
        self.ensemble = VotingClassifier(
            estimators=[(name, model) for name, model in self.models.items()],
            voting='soft',
            weights=[1.0, 1.2, 1.1, 0.8, 0.9]  # Weighted voting
        )
        
        self.ensemble.fit(X, y)
        self.classes_ = self.ensemble.classes_
        
        return self
    
    def predict(self, X):
        """Make predictions"""
        return self.ensemble.predict(X)
    
    def predict_proba(self, X):
        """Get prediction probabilities"""
        return self.ensemble.predict_proba(X)
    
    def get_model_performance(self, X_test, y_test):
        """Get individual model performance"""
        from sklearn.metrics import accuracy_score
        
        performances = {}
        for name, model in self.models.items():
            if hasattr(model, 'predict'):
                preds = model.predict(X_test)
                acc = accuracy_score(y_test, preds)
                performances[name] = acc
                print(f"{name}: {acc:.2%}")
        
        # Ensemble performance
        ensemble_preds = self.predict(X_test)
        ensemble_acc = accuracy_score(y_test, ensemble_preds)
        performances['ensemble'] = ensemble_acc
        print(f"Ensemble: {ensemble_acc:.2%}")
        
        return performances