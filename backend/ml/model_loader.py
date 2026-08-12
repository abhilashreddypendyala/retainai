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

    def train_model(self):
        print("Training churn model as fallback...")
        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.preprocessing import StandardScaler
            
            data_path = os.path.join(BASE_DIR, "data", "processed", "master_customer_dataset.parquet")
            if not os.path.exists(data_path):
                print(f"Error: Dataset not found at {data_path}")
                return
                
            df = pd.read_parquet(data_path)
            
            feature_names = ["Recency", "Frequency", "Monetary", "Tenure", "Velocity", "AOV", "ItemDiversity"]
            target = "Churn"
            
            missing_cols = [col for col in feature_names + [target] if col not in df.columns]
            if missing_cols:
                print(f"Error: Missing required columns for training: {missing_cols}")
                return
                
            X = df[feature_names]
            y = df[target]
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            model = LogisticRegression(max_iter=1000)
            model.fit(X_scaled, y)
            
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(scaler, SCALER_PATH)
            joblib.dump(model, MODEL_PATH)
            print("Churn models successfully retrained and saved.")
        except Exception as e:
            print(f"Error during fallback training: {e}")

    def load(self):
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            self.train_model()
            
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
        else:
            print("Error: Churn models could not be loaded or generated.")

    def predict(self, features: list):
        if self.model is None or self.scaler is None:
            self.load()
            
        if self.model is None or self.scaler is None:
            raise ValueError("Churn model is not available for prediction.")
            
        feature_names = ["Recency", "Frequency", "Monetary", "Tenure", "Velocity", "AOV", "ItemDiversity"]
        X = pd.DataFrame([features], columns=feature_names)
        X_scaled = self.scaler.transform(X)
        
        prob = float(self.model.predict_proba(X_scaled)[0, 1])
        pred = int(self.model.predict(X_scaled)[0])
        
        return prob, pred

churn_model = ChurnModel()
