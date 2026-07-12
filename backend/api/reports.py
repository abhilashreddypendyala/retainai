from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from backend.schemas.report import ExecutiveSummary
import backend.services.report_service as service

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/executive-summary", response_model=ExecutiveSummary)
def get_executive_summary():
    """Returns high-level executive summary metrics."""
    return service.get_executive_summary()

@router.get("/customer-report", response_class=PlainTextResponse)
def get_customer_report():
    """Returns a full customer report as a CSV string."""
    return service.get_customer_report_csv()

@router.get("/high-risk", response_class=PlainTextResponse)
def get_high_risk_report():
    """Returns a report of high-risk customers as a CSV string."""
    return service.get_high_risk_report_csv()

@router.get("/segment-summary", response_class=PlainTextResponse)
def get_segment_summary():
    """Returns a summary of customer segments as a CSV string."""
    return service.get_segment_summary_csv()
