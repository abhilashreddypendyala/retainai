from fastapi import APIRouter
from typing import List
from backend.schemas.dashboard import (
    DashboardSummary, 
    DashboardCharts, 
    DashboardIntervention, 
    ModelSummary
)
import backend.services.dashboard_service as service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/summary", response_model=DashboardSummary)
def get_summary():
    """Returns dashboard KPI cards."""
    return service.get_dashboard_summary()

@router.get("/charts", response_model=DashboardCharts)
def get_charts():
    """Returns all chart data required by the dashboard."""
    return service.get_dashboard_charts()

@router.get("/interventions", response_model=List[DashboardIntervention])
def get_interventions():
    """Returns the current intervention table including customers requiring immediate retention actions."""
    return service.get_dashboard_interventions()

@router.get("/model-summary", response_model=ModelSummary)
def get_model_summary():
    """Return model information from model_metadata."""
    return service.get_model_summary()
