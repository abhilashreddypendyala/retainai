from backend.schemas.prediction import PredictionRequest, PredictionResponse
from backend.ml.model_loader import churn_model

def _get_risk_level(prob: float) -> str:
    if prob < 0.3:
        return "Low"
    elif prob < 0.7:
        return "Medium"
    else:
        return "High"

def generate_prediction(req: PredictionRequest) -> PredictionResponse:
    features = [
        req.Recency,
        req.Frequency,
        req.Monetary,
        req.Tenure,
        req.Velocity,
        req.AOV,
        req.ItemDiversity
    ]
    
    prob, pred = churn_model.predict(features)
    
    return PredictionResponse(
        churn_probability=prob,
        churn_prediction=pred,
        confidence_score=max(prob, 1 - prob),
        risk_level=_get_risk_level(prob)
    )
