from pydantic import BaseModel
from typing import List, Optional

class CustomerSummary(BaseModel):
    customer_id: str
    country: Optional[str] = "Unknown"
    segment: Optional[str]
    clv: float
    churn_probability: float
    churn_prediction: int

class CustomerProfile(BaseModel):
    customer_id: str
    country: Optional[str] = "Unknown"
    segment: Optional[str]
    clv: float
    churn_probability: float
    churn_prediction: int
    recency: int
    frequency: int
    monetary: float
    purchase_frequency: float
    avg_order_value: float
    customer_lifespan: int
    item_diversity: int

class CustomerListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[CustomerSummary]

class TransactionItem(BaseModel):
    invoice: str
    date: str
    description: str
    quantity: int
    unit_price: float
    total_amount: float

class Recommendation(BaseModel):
    priority: str
    action: str
    reason: str
    estimated_roi: str

class Customer360Response(BaseModel):
    customer: CustomerProfile
    recent_transactions: List[TransactionItem]
    recommendation: Recommendation
