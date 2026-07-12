import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_DIR = "database"
DB_PATH = os.path.join(DB_DIR, "retail.db")

def create_database():
    # Ensure database directory exists
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create customers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        recency INTEGER,
        frequency INTEGER,
        monetary REAL,
        avg_order_value REAL,
        purchase_frequency REAL,
        customer_lifespan INTEGER,
        clv REAL,
        churn_probability REAL,
        churn_prediction INTEGER,
        segment TEXT,
        item_diversity INTEGER
    )
    ''')

    # 2. Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        invoice TEXT,
        stock_code TEXT,
        description TEXT,
        quantity INTEGER,
        invoice_date TIMESTAMP,
        unit_price REAL,
        customer_id TEXT,
        country TEXT,
        total_amount REAL,
        date TIMESTAMP
    )
    ''')

    # 3. Create predictions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        prediction_type TEXT,
        prediction REAL,
        confidence REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. Create model_metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS model_metadata (
        model_name TEXT,
        version TEXT,
        algorithm TEXT,
        accuracy REAL,
        precision REAL,
        recall REAL,
        f1_score REAL,
        roc_auc REAL,
        trained_on DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()

    # Data Import
    
    # Load and map customers
    print("Loading parquet files...")
    df_customers = pd.read_parquet('data/processed/master_customer_dataset.parquet')
    
    df_customers = df_customers.rename(columns={
        'CustomerID': 'customer_id',
        'Recency': 'recency',
        'Frequency': 'frequency',
        'Monetary': 'monetary',
        'AOV': 'avg_order_value',
        'Velocity': 'purchase_frequency',
        'Tenure': 'customer_lifespan',
        'predicted_90d_clv': 'clv',
        'Churn_Probability': 'churn_probability',
        'Churn': 'churn_prediction',
        'Segment': 'segment',
        'ItemDiversity': 'item_diversity'
    })
    
    # Ensure one row per customer
    df_customers = df_customers.drop_duplicates(subset=['customer_id'])

    # Clear existing data in tables to ensure idempotency for script re-runs
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM model_metadata")
    conn.commit()

    # Load and map transactions
    df_transactions = pd.read_parquet('data/processed/cleaned_online_retail.parquet')
    
    df_transactions = df_transactions.rename(columns={
        'InvoiceNo': 'invoice',
        'StockCode': 'stock_code',
        'Description': 'description',
        'Quantity': 'quantity',
        'InvoiceDate': 'invoice_date',
        'UnitPrice': 'unit_price',
        'CustomerID': 'customer_id',
        'Country': 'country',
        'TotalAmount': 'total_amount',
        'Date': 'date'
    })

    # Insert data using pandas
    print("Inserting customers...")
    df_customers.to_sql('customers', conn, if_exists='append', index=False)
    customers_inserted = len(df_customers)
    
    print("Inserting transactions...")
    df_transactions.to_sql('transactions', conn, if_exists='append', index=False)
    transactions_inserted = len(df_transactions)

    # Insert model metadata placeholder row
    cursor.execute('''
        INSERT INTO model_metadata (
            model_name, version, algorithm, accuracy, precision, recall, f1_score, roc_auc, trained_on
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Churn Prediction Model', '1.0', 'Logistic Regression', 0.85, 0.82, 0.80, 0.81, 0.88, datetime.now()))
    conn.commit()
    
    conn.close()

    # Print summary
    print(f"\nCustomers inserted: {customers_inserted}")
    print(f"Transactions inserted: {transactions_inserted}")
    print("Predictions table created")
    print("Model metadata inserted")
    print("Database created successfully.")

if __name__ == "__main__":
    create_database()
