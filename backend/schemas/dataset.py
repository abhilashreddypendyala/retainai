from pydantic import BaseModel, Field
from typing import List, Dict, Any

class KPISummary(BaseModel):
    total_customers: int
    total_transactions: int
    total_revenue: float
    average_predicted_clv: float
    high_risk_customers: int
    medium_risk_customers: int
    low_risk_customers: int
    vip_customers: int

class CustomerPredictionRecord(BaseModel):
    customer_id: str
    country: str
    clv: float
    churn_probability: float
    churn_prediction: int
    risk_level: str
    segment: str
    is_vip: int
    recency: float
    frequency: float
    monetary: float
    tenure: float
    velocity: float
    aov: float
    item_diversity: float

class DatasetAnalysisResponse(BaseModel):
    kpi_summary: KPISummary
    distributions: Dict[str, Dict[str, Any]]
    top_customers: List[Dict[str, Any]]
    customers: List[Dict[str, Any]]
