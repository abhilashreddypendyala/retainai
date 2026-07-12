from pydantic import BaseModel
from typing import List

class DashboardSummary(BaseModel):
    total_customers: int
    total_revenue: float
    projected_revenue: float
    revenue_at_risk: float
    high_risk_customers: int

class RevenueTrend(BaseModel):
    date: str
    revenue: float

class SegmentDistribution(BaseModel):
    segment: str
    count: int

class RiskValueScatter(BaseModel):
    customer_id: str
    clv: float
    churn_probability: float
    segment: str

class DashboardCharts(BaseModel):
    revenue_trend: List[RevenueTrend]
    segment_distribution: List[SegmentDistribution]
    risk_vs_value: List[RiskValueScatter]

class DashboardIntervention(BaseModel):
    customer_id: str
    segment: str
    clv: float
    churn_probability: float
    recency: int
    frequency: int
    monetary: float

class ModelSummary(BaseModel):
    model_name: str
    algorithm: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    trained_on: str
