import pandas as pd
from datetime import datetime
from backend.database.connection import get_db_connection
from backend.schemas.report import ExecutiveSummary

def get_executive_summary() -> ExecutiveSummary:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*), SUM(monetary), AVG(clv) FROM customers")
        total_customers, total_revenue, average_clv = cur.fetchone()
        
        cur.execute("SELECT COUNT(*), SUM(monetary) FROM customers WHERE churn_prediction = 1")
        high_risk_customers, revenue_at_risk = cur.fetchone()
        
        return ExecutiveSummary(
            total_customers=total_customers or 0,
            high_risk_customers=high_risk_customers or 0,
            total_revenue=total_revenue or 0.0,
            revenue_at_risk=revenue_at_risk or 0.0,
            average_clv=average_clv or 0.0,
            generated_timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    finally:
        conn.close()

def get_customer_report_csv() -> str:
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            c.customer_id as 'Customer ID', 
            COALESCE(t.country, 'Unknown') as 'Country', 
            c.segment as 'Segment', 
            c.clv as 'CLV', 
            c.churn_probability as 'Churn Probability', 
            CASE WHEN c.churn_prediction = 1 THEN 'Win-Back Campaign (High Risk)' ELSE 'Loyalty Program (Safe)' END as 'Recommendation'
        FROM customers c
        LEFT JOIN (
            SELECT customer_id, MAX(country) as country FROM transactions GROUP BY customer_id
        ) t ON c.customer_id = t.customer_id
        """
        df = pd.read_sql_query(query, conn)
        return df.to_csv(index=False)
    finally:
        conn.close()

def get_high_risk_report_csv() -> str:
    conn = get_db_connection()
    try:
        query = """
        SELECT * 
        FROM customers 
        WHERE churn_prediction = 1
        """
        df = pd.read_sql_query(query, conn)
        return df.to_csv(index=False)
    finally:
        conn.close()

def get_segment_summary_csv() -> str:
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            segment as 'Segment', 
            COUNT(*) as 'Customer Count', 
            AVG(clv) as 'Average CLV', 
            SUM(monetary) as 'Total Revenue'
        FROM customers
        GROUP BY segment
        """
        df = pd.read_sql_query(query, conn)
        return df.to_csv(index=False)
    finally:
        conn.close()
