from fastapi import APIRouter, Query, Path, HTTPException
from typing import List, Optional
from backend.schemas.customer import CustomerSummary, CustomerProfile, CustomerListResponse, Customer360Response
import backend.services.customer_service as service

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("", response_model=CustomerListResponse)
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    sim_risk: Optional[float] = Query(None, description="Dynamic churn risk threshold"),
    sim_clv: Optional[float] = Query(None, description="Dynamic high-value CLV cutoff")
):
    """Return a paginated customer list."""
    return service.get_customers(page, page_size, sim_risk, sim_clv)

@router.get("/ids", response_model=List[str])
def get_all_customer_ids():
    """Return a flat list of all customer IDs for the frontend dropdown."""
    return service.get_all_customer_ids()

@router.get("/search", response_model=List[CustomerSummary])
def search_customers(
    q: str = Query(..., min_length=1, description="Partial customer ID search term"),
    sim_risk: Optional[float] = Query(None, description="Dynamic churn risk threshold"),
    sim_clv: Optional[float] = Query(None, description="Dynamic high-value CLV cutoff")
):
    """Search customers by partial ID match."""
    return service.search_customers(q, sim_risk, sim_clv)

@router.get("/filter", response_model=List[CustomerSummary])
def filter_customers(
    segment: Optional[str] = Query(None, description="Filter by segment"),
    country: Optional[str] = Query(None, description="Filter by country"),
    churn_prediction: Optional[int] = Query(None, description="Filter by churn prediction (0 or 1)"),
    sim_risk: Optional[float] = Query(None, description="Dynamic churn risk threshold"),
    sim_clv: Optional[float] = Query(None, description="Dynamic high-value CLV cutoff")
):
    """Filter customers by segment, country, or churn prediction."""
    if churn_prediction is not None and churn_prediction not in [0, 1]:
        raise HTTPException(status_code=400, detail="Invalid churn_prediction. Must be 0 or 1.")
    return service.filter_customers(segment, country, churn_prediction, sim_risk, sim_clv)

@router.get("/{customer_id}", response_model=Customer360Response)
def get_customer(
    customer_id: str = Path(..., description="The ID of the customer to retrieve"),
    sim_risk: Optional[float] = Query(None, description="Dynamic churn risk threshold"),
    sim_clv: Optional[float] = Query(None, description="Dynamic high-value CLV cutoff")
):
    """Return the complete Customer 360 profile."""
    return service.get_customer_by_id(customer_id, sim_risk, sim_clv)
