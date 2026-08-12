import os
import pandas as pd
import numpy as np
import warnings
from typing import Tuple
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CLV_MODEL_DIR = os.path.join(BASE_DIR, "models", "clv")
BGF_PATH = os.path.join(CLV_MODEL_DIR, "bgf_model.pkl")
GGF_PATH = os.path.join(CLV_MODEL_DIR, "ggf_model.pkl")
HISTORICAL_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_online_retail.parquet")

class CLVModelLoader:
    """
    Stage 2: Analytics - CLV ML Inference Engine
    Manages loading of persisted BetaGeoFitter (BG/NBD) and GammaGammaFitter models using native Lifetimes serialization.
    If persisted models don't exist yet, trains them once on the historical benchmark dataset and saves them.
    Never retrains immediately on user inference uploads.
    """
    def __init__(self):
        self.bgf = None
        self.ggf = None

    def load_or_train(self):
        if os.path.exists(BGF_PATH) and os.path.exists(GGF_PATH):
            self.bgf = BetaGeoFitter()
            self.bgf.load_model(BGF_PATH)
            self.ggf = GammaGammaFitter()
            self.ggf.load_model(GGF_PATH)
            return

        # Models do not exist yet; train once using the verified historical training dataset
        if not os.path.exists(CLV_MODEL_DIR):
            os.makedirs(CLV_MODEL_DIR, exist_ok=True)

        if not os.path.exists(HISTORICAL_DATA_PATH):
            raise FileNotFoundError(f"Cannot initialize CLV models: Historical training dataset not found at {HISTORICAL_DATA_PATH}")

        print("Persisting CLV models for the first time using historical benchmark dataset...")
        df_raw = pd.read_parquet(HISTORICAL_DATA_PATH)
        clv_data = summary_data_from_transaction_data(
            df_raw, 'CustomerID', 'InvoiceDate', monetary_value_col='TotalAmount',
            observation_period_end=df_raw['Date'].max()
        )

        # Fit BG/NBD Model with robust penalizer values for clean convergence
        bgf = None
        for pen in [0.1, 0.5, 1.0, 5.0]:
            try:
                temp_bgf = BetaGeoFitter(penalizer_coef=pen)
                temp_bgf.fit(clv_data['frequency'], clv_data['recency'], clv_data['T'])
                if not np.isnan(temp_bgf.params_).any():
                    bgf = temp_bgf
                    break
            except Exception:
                continue

        if bgf is None:
            bgf = BetaGeoFitter(penalizer_coef=1.0)
            bgf.fit(clv_data['frequency'], clv_data['recency'], clv_data['T'])

        # Fit Gamma-Gamma Model on returning customers
        returning = clv_data[clv_data['frequency'] > 0]
        ggf = None
        for pen in [0.01, 0.1, 0.5, 1.0]:
            try:
                temp_ggf = GammaGammaFitter(penalizer_coef=pen)
                temp_ggf.fit(returning['frequency'], returning['monetary_value'])
                if not np.isnan(temp_ggf.params_).any():
                    ggf = temp_ggf
                    break
            except Exception:
                continue

        if ggf is None:
            ggf = GammaGammaFitter(penalizer_coef=1.0)
            ggf.fit(returning['frequency'], returning['monetary_value'])

        # Save trained models using native Lifetimes serialization
        bgf.save_model(BGF_PATH)
        ggf.save_model(GGF_PATH)
        
        self.bgf = bgf
        self.ggf = ggf
        print("CLV models successfully saved to models/clv/")

    def predict_batch(self, df_raw: pd.DataFrame, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Executes pure inference using pre-trained BG/NBD and Gamma-Gamma models without retraining.
        Computes 90-Day Predicted Customer Lifetime Value.
        """
        if self.bgf is None or self.ggf is None:
            self.load_or_train()

        df_out = df_features.copy()
        
        try:
            # Transform inference transactions into Lifetimes RFM format
            clv_summary = summary_data_from_transaction_data(
                df_raw, 'CustomerID', 'InvoiceDate', monetary_value_col='TotalAmount',
                observation_period_end=df_raw['Date'].max()
            ).reset_index()

            # Predict repeat transaction volume in next 90 days
            clv_summary['predicted_purchases_90d'] = self.bgf.predict(
                90, clv_summary['frequency'], clv_summary['recency'], clv_summary['T']
            )

            # Predict expected average transaction value
            # For returning customers (frequency > 0), use GammaGamma model
            cond_returning = clv_summary['frequency'] > 0
            clv_summary['predicted_aov'] = clv_summary['monetary_value'] # fallback default
            
            if cond_returning.any():
                clv_summary.loc[cond_returning, 'predicted_aov'] = self.ggf.conditional_expected_average_profit(
                    clv_summary.loc[cond_returning, 'frequency'],
                    clv_summary.loc[cond_returning, 'monetary_value']
                )

            # 90-Day CLV = Volume * Value
            clv_summary['clv'] = clv_summary['predicted_purchases_90d'] * clv_summary['predicted_aov']
            clv_summary['clv'] = clv_summary['clv'].apply(lambda x: max(float(x), 0.0))
            
            # Merge predicted CLV back into feature dataframe
            df_out = pd.merge(df_out, clv_summary[['CustomerID', 'clv']], on='CustomerID', how='left')
        except Exception as e:
            print(f"Notice during Lifetimes inference: {e}. Using empirical revenue projection.")
            df_out['clv'] = np.nan

        # Fill any missing/NaN CLV estimations with empirical 90-day trajectory
        if 'clv' not in df_out.columns or df_out['clv'].isnull().any():
            fallback_clv = (df_out['Monetary'] / np.maximum(df_out['Tenure'], 30.0)) * 90.0
            if 'clv' not in df_out.columns:
                df_out['clv'] = fallback_clv
            else:
                df_out['clv'] = df_out['clv'].fillna(fallback_clv)

        df_out['clv'] = df_out['clv'].apply(lambda x: max(float(x), 0.0))
        return df_out

clv_model_loader = CLVModelLoader()
