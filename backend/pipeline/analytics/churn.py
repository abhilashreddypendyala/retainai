import pandas as pd
import numpy as np
from backend.ml.model_loader import churn_model

def _map_risk_level(prob: float) -> str:
    if prob >= 0.5:
        return "High"
    elif prob >= 0.3:
        return "Medium"
    else:
        return "Low"

def predict_batch_churn(df_features: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2: Analytics - Batch Churn Inference Engine
    Reuses the existing Champion Logistic Regression Model (lr_champion.pkl) and feature_scaler.pkl without retraining.
    Computes exact granular churn probabilities and assigns Risk Level classifications.
    """
    df_out = df_features.copy()
    
    if churn_model.model is None or churn_model.scaler is None:
        churn_model.load()

    feature_names = ["Recency", "Frequency", "Monetary", "Tenure", "Velocity", "AOV", "ItemDiversity"]
    
    # Ensure all required features exist and are numeric
    for col in feature_names:
        if col not in df_out.columns:
            df_out[col] = 0.0
        df_out[col] = pd.to_numeric(df_out[col], errors='coerce').fillna(0.0)

    X = df_out[feature_names]
    X_scaled = churn_model.scaler.transform(X)

    probs = churn_model.model.predict_proba(X_scaled)[:, 1]
    preds = churn_model.model.predict(X_scaled)

    df_out['churn_probability'] = probs
    df_out['churn_prediction'] = preds.astype(int)
    df_out['risk_level'] = df_out['churn_probability'].apply(_map_risk_level)
    df_out['confidence_score'] = df_out['churn_probability'].apply(lambda p: float(max(p, 1.0 - p)))

    return df_out
