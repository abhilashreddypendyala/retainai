from fastapi import HTTPException
from backend.database.connection import get_db_connection, close_db_connection
from backend.schemas.dashboard import (
    DashboardSummary, 
    DashboardCharts, 
    DashboardIntervention, 
    ModelSummary,
    RevenueTrend,
    SegmentDistribution,
    RiskValueScatter
)

def get_dashboard_summary() -> DashboardSummary:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_customers = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT SUM(total_amount) FROM transactions")
        total_revenue = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(clv) FROM customers")
        projected_revenue = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT SUM(clv) FROM customers WHERE churn_prediction = 1")
        revenue_at_risk = cursor.fetchone()[0] or 0.0
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE churn_prediction = 1")
        high_risk_customers = cursor.fetchone()[0] or 0
        
        return DashboardSummary(
            total_customers=total_customers,
            total_revenue=total_revenue,
            projected_revenue=projected_revenue,
            revenue_at_risk=revenue_at_risk,
            high_risk_customers=high_risk_customers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def get_dashboard_charts() -> DashboardCharts:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Revenue trend (Monthly)
        cursor.execute("""
            SELECT strftime('%Y-%m', invoice_date) as month, SUM(total_amount) as revenue 
            FROM transactions 
            GROUP BY month 
            ORDER BY month
        """)
        revenue_trend = [RevenueTrend(date=row['month'] if row['month'] else "Unknown", revenue=row['revenue']) for row in cursor.fetchall()]
        
        # Segment distribution
        cursor.execute("""
            SELECT segment, COUNT(*) as count 
            FROM customers 
            GROUP BY segment
        """)
        segment_distribution = [SegmentDistribution(segment=row['segment'] or "Unknown", count=row['count']) for row in cursor.fetchall()]
        
        # Risk vs Value Scatter
        cursor.execute("""
            SELECT customer_id, clv, churn_probability, segment 
            FROM customers
        """)
        risk_vs_value = [RiskValueScatter(
            customer_id=str(row['customer_id']),
            clv=row['clv'],
            churn_probability=row['churn_probability'],
            segment=row['segment'] or "Unknown"
        ) for row in cursor.fetchall()]
        
        return DashboardCharts(
            revenue_trend=revenue_trend,
            segment_distribution=segment_distribution,
            risk_vs_value=risk_vs_value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def get_dashboard_interventions() -> list[DashboardIntervention]:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Fetch all customers to allow frontend interactive filtering
        cursor.execute("""
            SELECT customer_id, segment, clv, churn_probability, recency, frequency, monetary 
            FROM customers 
            ORDER BY clv DESC 
        """)
        interventions = [DashboardIntervention(
            customer_id=str(row['customer_id']),
            segment=row['segment'] or "Unknown",
            clv=row['clv'],
            churn_probability=row['churn_probability'],
            recency=row['recency'],
            frequency=row['frequency'],
            monetary=row['monetary']
        ) for row in cursor.fetchall()]
        
        return interventions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)

def get_model_summary() -> ModelSummary:
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT model_name, algorithm, accuracy, precision, recall, f1_score, roc_auc, trained_on 
            FROM model_metadata 
            ORDER BY trained_on DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Model metadata not found")
            
        return ModelSummary(
            model_name=row['model_name'],
            algorithm=row['algorithm'],
            accuracy=row['accuracy'],
            precision=row['precision'],
            recall=row['recall'],
            f1_score=row['f1_score'],
            roc_auc=row['roc_auc'],
            trained_on=str(row['trained_on'])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        close_db_connection(conn)
