import pandas as pd
import numpy as np
from typing import Dict, Any, List

from backend.pipeline.preprocessing.cleaning import validate_and_clean_data
from backend.pipeline.preprocessing.rfm import generate_rfm
from backend.pipeline.preprocessing.feature_engineering import generate_advanced_features
from backend.pipeline.analytics.clv import clv_model_loader
from backend.pipeline.analytics.churn import predict_batch_churn
from backend.pipeline.analytics.segmentation import assign_customer_segments

def run_dataset_intelligence(df_raw_input: pd.DataFrame) -> Dict[str, Any]:
    """
    Master Orchestrator for RETAIN-AI Dataset Intelligence & Batch Pipeline.
    Executes Stage 1 (Preprocessing) followed sequentially by Stage 2 (Analytics).
    Returns rich customer predictions and dataset KPI summaries in-memory without mutating the production database.
    """
    # Stage 1: Preprocessing Pipeline
    df_clean = validate_and_clean_data(df_raw_input)
    df_rfm = generate_rfm(df_clean)
    df_features = generate_advanced_features(df_clean, df_rfm)

    # Stage 2: Analytics Pipeline
    df_clv = clv_model_loader.predict_batch(df_clean, df_features)
    df_churn = predict_batch_churn(df_clv)
    df_final = assign_customer_segments(df_churn)

    # Clean field names for API standard compliance
    df_final = df_final.rename(columns={
        'CustomerID': 'customer_id',
        'Country': 'country',
        'Recency': 'recency',
        'Frequency': 'frequency',
        'Monetary': 'monetary',
        'Tenure': 'tenure',
        'Velocity': 'velocity',
        'AOV': 'aov',
        'ItemDiversity': 'item_diversity'
    })

    # Convert numeric columns to Python float/int to prevent JSON serialization errors
    for col in ['recency', 'frequency', 'monetary', 'tenure', 'velocity', 'aov', 'item_diversity', 'clv', 'churn_probability', 'confidence_score']:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(float)

    for col in ['churn_prediction', 'is_vip']:
        if col in df_final.columns:
            df_final[col] = df_final[col].astype(int)

    # Compute KPI Summaries required for Business Dashboard
    total_customers = int(len(df_final))
    total_transactions = int(df_clean['InvoiceNo'].nunique())
    total_revenue = float(df_clean['TotalAmount'].sum())
    avg_clv = float(df_final['clv'].mean()) if total_customers > 0 else 0.0

    high_risk_count = int((df_final['risk_level'] == 'High').sum())
    medium_risk_count = int((df_final['risk_level'] == 'Medium').sum())
    low_risk_count = int((df_final['risk_level'] == 'Low').sum())
    vip_count = int((df_final['is_vip'] == 1).sum())

    kpi_summary = {
        "total_customers": total_customers,
        "total_transactions": total_transactions,
        "total_revenue": total_revenue,
        "average_predicted_clv": avg_clv,
        "high_risk_customers": high_risk_count,
        "medium_risk_customers": medium_risk_count,
        "low_risk_customers": low_risk_count,
        "vip_customers": vip_count
    }

    # Chart Distributions
    risk_distribution = df_final['risk_level'].value_counts().to_dict()
    segment_distribution = df_final['segment'].value_counts().to_dict()

    # Top Customers by CLV (limit to top 100 for table display)
    top_customers_df = df_final.sort_values(by="clv", ascending=False).head(100)
    
    # Sort entire dataset by CLV descending for CSV export
    df_sorted = df_final.sort_values(by="clv", ascending=False)
    customers_list = df_sorted.to_dict(orient="records")
    top_customers_list = top_customers_df.to_dict(orient="records")

    return {
        "kpi_summary": kpi_summary,
        "distributions": {
            "risk": risk_distribution,
            "segments": segment_distribution
        },
        "top_customers": top_customers_list,
        "customers": customers_list
    }
