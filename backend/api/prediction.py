from fastapi import APIRouter
from backend.schemas.prediction import PredictionRequest, PredictionResponse
import backend.services.prediction_service as service

router = APIRouter(prefix="/prediction", tags=["Prediction"])

@router.post("", response_model=PredictionResponse)
def get_prediction(req: PredictionRequest):
    """Generate a live churn prediction using the ML model."""
    return service.generate_prediction(req)
