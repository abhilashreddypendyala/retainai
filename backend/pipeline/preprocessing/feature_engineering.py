import pandas as pd
import numpy as np

def generate_advanced_features(df_raw: pd.DataFrame, df_rfm: pd.DataFrame, cutoff_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    Stage 1: Preprocessing - Advanced Behavioral Feature Engineering
    Refactored directly from research notebook 03_advanced_feature_engineering.ipynb.
    Computes Tenure, Velocity, Average Order Value (AOV), and Item Diversity.
    """
    if cutoff_date is None:
        cutoff_date = df_raw['Date'].max()

    df_advanced = df_rfm.copy()

    # 1. Tenure (days between first purchase and cutoff)
    first_purchase = df_raw.groupby('CustomerID')['Date'].min().reset_index()
    first_purchase.rename(columns={'Date': 'FirstPurchaseDate'}, inplace=True)
    first_purchase['Tenure'] = (cutoff_date - first_purchase['FirstPurchaseDate']).dt.days
    first_purchase['Tenure'] = first_purchase['Tenure'].apply(lambda t: max(float(t), 0.0))

    df_advanced = pd.merge(df_advanced, first_purchase[['CustomerID', 'Tenure']], on='CustomerID', how='left')

    # 2. Purchase Velocity (average days between orders)
    # If bought once (Frequency == 1), velocity equals entire tenure
    df_advanced['Velocity'] = np.where(
        df_advanced['Frequency'] > 1,
        df_advanced['Tenure'] / df_advanced['Frequency'],
        df_advanced['Tenure']
    ).astype(float)

    # 3. Average Order Value (AOV)
    df_advanced['AOV'] = (df_advanced['Monetary'] / df_advanced['Frequency']).astype(float)

    # 4. Item Diversity (number of unique product items bought)
    diversity = df_raw.groupby('CustomerID')['StockCode'].nunique().reset_index()
    diversity.rename(columns={'StockCode': 'ItemDiversity'}, inplace=True)
    df_advanced = pd.merge(df_advanced, diversity, on='CustomerID', how='left')
    df_advanced['ItemDiversity'] = df_advanced['ItemDiversity'].fillna(1.0).astype(float)

    # Clean any potential NaNs or infinite values from division
    df_advanced.fillna(0.0, inplace=True)
    df_advanced.replace([np.inf, -np.inf], 0.0, inplace=True)

    # Pipeline Assertions
    assert df_advanced['Tenure'].min() >= 0, "Pipeline Error: Negative Tenure detected!"
    assert df_advanced['AOV'].min() >= 0, "Pipeline Error: Negative AOV detected!"
    assert df_advanced['Velocity'].isnull().sum() == 0, "Pipeline Error: Nulls found in Velocity!"
    assert len(df_advanced) == len(df_rfm), "Pipeline Error: Customer count mismatch during feature engineering merge!"

    return df_advanced
