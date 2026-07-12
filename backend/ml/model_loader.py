import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "models", "churn", "lr_champion.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "models", "churn", "feature_scaler.pkl")

class ChurnModel:
    def __init__(self):
        self.model = None
        self.scaler = None

    def load(self):
        self.model = joblib.load(MODEL_PATH)
        self.scaler = joblib.load(SCALER_PATH)

    def predict(self, features: list):
        if self.model is None or self.scaler is None:
            self.load()
            
        feature_names = ["Recency", "Frequency", "Monetary", "Tenure", "Velocity", "AOV", "ItemDiversity"]
        X = pd.DataFrame([features], columns=feature_names)
        X_scaled = self.scaler.transform(X)
        
        prob = float(self.model.predict_proba(X_scaled)[0, 1])
        pred = int(self.model.predict(X_scaled)[0])
        
        return prob, pred

churn_model = ChurnModel()
