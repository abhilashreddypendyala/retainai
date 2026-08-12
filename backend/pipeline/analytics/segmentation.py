import pandas as pd
import numpy as np

def assign_customer_segments(df_features: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 2: Analytics - Strategic Quadrant Segmentation
    Refactored directly from research notebook 06_customer_segmentation.ipynb.
    Assigns customers into the 4 strategic retention quadrants using exact 75th percentile CLV and 50% Churn Risk thresholds.
    """
    df_out = df_features

    # Calculate CLV threshold (Top 25% of predicted CLV)
    clv_threshold = df_out['clv'].quantile(0.75)
    if pd.isnull(clv_threshold) or clv_threshold <= 0:
        clv_threshold = df_out['clv'].mean() if df_out['clv'].mean() > 0 else 100.0

    risk_threshold = 0.50

    def get_segment(row) -> str:
        is_high_risk = row.get('churn_probability', 0.0) >= risk_threshold
        is_high_value = row.get('clv', 0.0) >= clv_threshold

        if is_high_risk and is_high_value:
            return "High-Risk Whales (Immediate Action)"
        elif not is_high_risk and is_high_value:
            return "Loyal Champions (Reward/Upsell)"
        elif is_high_risk and not is_high_value:
            return "At-Risk Regulars (Automated Win-back)"
        else:
            return "Safe Regulars (Monitor)"

    df_out['segment'] = df_out.apply(get_segment, axis=1)
    
    # Tag VIP Customers (anyone in the Top 25% High-Value tier)
    df_out['is_vip'] = df_out['segment'].isin([
        "High-Risk Whales (Immediate Action)",
        "Loyal Champions (Reward/Upsell)"
    ])

    return df_out
