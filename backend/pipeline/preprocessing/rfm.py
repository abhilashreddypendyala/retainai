import pandas as pd
import numpy as np

def generate_rfm(df: pd.DataFrame, cutoff_date: pd.Timestamp = None) -> pd.DataFrame:
    """
    Stage 1: Preprocessing - RFM Metric Calculation
    Refactored directly from research notebook 02_time_split_and_rfm.ipynb.
    Computes Recency (days from reference cutoff), Frequency (unique invoices), and Monetary value.
    """
    if cutoff_date is None:
        # For pure batch inference, calculate relative to the maximum date in the dataset
        cutoff_date = df['Date'].max()

    # Calculate RFM aggregations per customer
    rfm = df.groupby('CustomerID').agg({
        'Date': lambda x: (cutoff_date - x.max()).days,  # Recency: Days since last purchase
        'InvoiceNo': 'nunique',                          # Frequency: Count of unique invoices
        'TotalAmount': 'sum'                             # Monetary: Total customer spend
    }).reset_index()

    rfm.rename(columns={
        'Date': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalAmount': 'Monetary'
    }, inplace=True)

    # Ensure recency is non-negative
    rfm['Recency'] = rfm['Recency'].apply(lambda r: max(r, 0.0)).astype('float32')
    rfm['Frequency'] = rfm['Frequency'].astype('float32')
    rfm['Monetary'] = rfm['Monetary'].astype('float32')

    # Attach customer's primary country for reporting
    if 'Country' in df.columns:
        countries = df.groupby('CustomerID')['Country'].first().reset_index()
        rfm = pd.merge(rfm, countries, on='CustomerID', how='left')
    else:
        rfm['Country'] = 'Unknown'

    # Pipeline Assertions
    assert rfm['Recency'].min() >= 0, "Pipeline Error: Negative Recency detected in RFM calculation!"
    assert rfm['Frequency'].min() > 0, "Pipeline Error: Zero frequency detected in RFM calculation!"
    
    return rfm
