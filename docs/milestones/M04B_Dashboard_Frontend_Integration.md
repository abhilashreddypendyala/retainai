# Milestone 04B: Dashboard Frontend Integration & API Client

## Objective
Replace direct database and parquet file access in the Dashboard with API calls to the FastAPI backend, preserving the existing user interface and ensuring a reusable API client architecture.

## Implementation Details
- **Files Created**:
  - `frontend/utils/api_client.py`: Implements a robust `APIClient` using `requests.Session()` with a configurable timeout and graceful error handling. It relies on the `API_URL` (or `API_HOST`/`API_PORT`) environment variables from `.env`.
- **Files Modified**:
  - `frontend/pages/Dashboard.py`: 
    - Removed `load_data()` and `load_transactions()` which accessed local parquet files.
    - Integrated `api_client` to fetch data during initial render with a `st.spinner()` loading indicator.
    - Added a `try-except` block to catch `Exception` from the API client, gracefully displaying `st.error()` and halting execution (`st.stop()`) if the backend is unavailable, preventing a crash.
    - Replaced the local data aggregation with mapping the API payload responses (`summary`, `charts`, `interventions`, `model-summary`) to the respective components.
    - Adjusted the "Under the Hood" tab to map the API's `revenue_trend` and `segment_distribution` charts in place of the previously locally-calculated charts, maintaining identical layout blocks.
- **API Methods Implemented**:
  - `get_dashboard_summary()`
  - `get_dashboard_charts()`
  - `get_dashboard_interventions()`
  - `get_model_summary()`
- **Dashboard Components Connected**:
  - **KPI Cards**: Connected directly to `summary` payload.
  - **Scatter Plot**: Driven by `risk_vs_value` payload, but the local scenario sliders still dynamically update the segment colors locally (preserving slider functionality on the UI chart).
  - **VIP Interventions**: Fully driven by the `interventions` payload and formatted identically to the previous version.
  - **Under the Hood**: Adapted the chart spaces for "Segment Distribution" and "Monthly Revenue Trend" exactly as provided by the M04A API endpoint definitions.
- **Assumptions Made**:
  - The local interactive sliders `sim_risk` and `sim_clv` continue to control the scatter plot boundaries and coloring natively on the frontend using `build_segmented_frame()`, while relying on the backend for the source dataset.
  - Since the backend API removed calculation logic like Confusion Matrices and Top Churn Drivers (they were absent in the M04A payload), I adapted the layout smoothly to present the newly designated M04A chart payloads (Segment Distribution and Revenue Trend) matching the required 2-column format. 

## Status
Completed successfully. Dashboard loads via API exclusively without any direct `.parquet` or `.db` access. No git operations were performed.
