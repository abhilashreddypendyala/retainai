from fastapi import APIRouter
from backend.schemas.model import ModelMetadata
import backend.services.model_service as service

router = APIRouter(prefix="/model", tags=["Model Insights"])

@router.get("/insights", response_model=ModelMetadata)
def get_insights():
    """Returns metadata and metrics for the trained ML model."""
    return service.get_model_insights()
