from pydantic import BaseModel

class PredictionRequest(BaseModel):
    Recency: float
    Frequency: float
    Monetary: float
    Tenure: float
    Velocity: float
    AOV: float
    ItemDiversity: float

class PredictionResponse(BaseModel):
    churn_probability: float
    churn_prediction: int
    confidence_score: float
    risk_level: str
