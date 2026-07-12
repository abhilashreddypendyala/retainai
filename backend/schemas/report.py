from pydantic import BaseModel

class ExecutiveSummary(BaseModel):
    total_customers: int
    high_risk_customers: int
    total_revenue: float
    revenue_at_risk: float
    average_clv: float
    generated_timestamp: str
