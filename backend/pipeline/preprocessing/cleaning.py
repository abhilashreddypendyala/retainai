import pandas as pd
import numpy as np
from typing import Tuple

REQUIRED_COLUMNS = ['InvoiceNo', 'CustomerID', 'UnitPrice', 'Quantity', 'InvoiceDate']

COLUMN_MAPPING = {
    'Invoice': 'InvoiceNo',
    'invoiceno': 'InvoiceNo',
    'Customer ID': 'CustomerID',
    'customer_id': 'CustomerID',
    'customer id': 'CustomerID',
    'customerid': 'CustomerID',
    'Price': 'UnitPrice',
    'unitprice': 'UnitPrice',
    'unit_price': 'UnitPrice',
    'price': 'UnitPrice',
    'Stock Code': 'StockCode',
    'stockcode': 'StockCode',
    'stock_code': 'StockCode',
    'Invoice Date': 'InvoiceDate',
    'invoicedate': 'InvoiceDate',
    'invoice_date': 'InvoiceDate',
    'quantity': 'Quantity',
    'description': 'Description',
    'country': 'Country'
}

def validate_and_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Stage 1: Preprocessing - Validation and Data Cleaning
    Refactored directly from research notebook 01_data_preprocessing_and_cleaning.ipynb.
    Standardizes schema, removes invalid transactions, cancellations, and computes TotalAmount.
    """
    df = df.copy()
    
    # 1. Standardize column names
    df.rename(columns=lambda col: COLUMN_MAPPING.get(col, COLUMN_MAPPING.get(str(col).strip(), col)), inplace=True)
    # Also check case-insensitive matches if needed
    col_dict = {col.lower().strip(): col for col in df.columns}
    for k, v in COLUMN_MAPPING.items():
        if k.lower().strip() in col_dict and col_dict[k.lower().strip()] not in df.columns:
            df.rename(columns={col_dict[k.lower().strip()]: v}, inplace=True)
            
    # Check for required columns
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Dataset validation failed. Missing required columns: {', '.join(missing)}")
        
    # Ensure Country and StockCode exist even if optional in raw variations
    if 'Country' not in df.columns:
        df['Country'] = 'Unknown'
    if 'StockCode' not in df.columns:
        df['StockCode'] = 'ITEM'
    if 'Description' not in df.columns:
        df['Description'] = 'Product Item'

    # 2. Missing value treatment: Drop rows without CustomerID
    df = df.dropna(subset=['CustomerID']).copy()
    
    if df.empty:
        raise ValueError("Dataset validation failed: No valid records remaining after dropping null Customer IDs.")

    # 3. Format Data Types
    df['InvoiceNo'] = df['InvoiceNo'].astype(str)
    df['StockCode'] = df['StockCode'].astype(str)
    
    # Handle floats like 12345.0 by converting to numeric then int then str
    def clean_id(val):
        try:
            return str(int(float(val)))
        except (ValueError, TypeError):
            return str(val).strip()
            
    df['CustomerID'] = df['CustomerID'].apply(clean_id)
    df = df[df['CustomerID'] != '0']

    # 4. Anomaly Removal: Filter out cancellations (starting with 'C' or 'c') and systemic errors
    df = df[~df['InvoiceNo'].str.upper().str.startswith('C')]
    
    # Convert numeric columns safely
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
    df['UnitPrice'] = pd.to_numeric(df['UnitPrice'], errors='coerce').fillna(0)
    
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    if df.empty:
        raise ValueError("Dataset validation failed: No valid transactions remaining after anomaly and cancellation filtering.")

    # 5. Base Feature Engineering
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df = df.dropna(subset=['InvoiceDate'])
    
    if df.empty:
        raise ValueError("Dataset validation failed: Invalid InvoiceDate formats across all records.")

    df['Date'] = pd.to_datetime(df['InvoiceDate'].dt.date)
    
    # Pipeline Assertions
    assert df['Quantity'].min() > 0, "Pipeline Error: Negative quantities detected after cleaning!"
    assert df['TotalAmount'].min() > 0, "Pipeline Error: Negative amounts detected after cleaning!"
    assert df['CustomerID'].isnull().sum() == 0, "Pipeline Error: Null IDs detected after cleaning!"
    
    return df
