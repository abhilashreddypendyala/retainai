# Milestone 08: Reports & Export Center

## Objective
Finalize the RetainAI platform by implementing a dedicated Reports & Export Center. This module allows business stakeholders to download aggregate data, live prediction histories, and filtered customer subsets for offline analysis or presentations.

## Architecture & Integration
- **Strict Backend Isolation**: The frontend remains stateless and completely decoupled from SQLite. The Streamlit app relies exclusively on the FastAPI endpoints (via `api_client.py`) to retrieve report payloads.
- **REST Streaming**: Four new endpoints were registered under `backend/api/reports.py`. Three of these endpoints (`/customer-report`, `/high-risk`, and `/segment-summary`) stream their data directly as `text/csv` using `PlainTextResponse`. 
- **Session State Interaction**: The Prediction History report dynamically builds a CSV exclusively from Streamlit's `st.session_state`, ensuring cross-page data consistency without needing to commit raw prediction logs to the production database.

## Components Created

### 1. Backend Schemas & Service (`backend/schemas/report.py`, `backend/services/report_service.py`)
- **Executive Summary**: Created a dedicated `ExecutiveSummary` Pydantic model. The service executes aggregate SQL functions (`COUNT`, `SUM`, `AVG`) across the `customers` table to compute total revenue, revenue at risk, and average CLV.
- **CSV Data Pipelines**: Utilized `pandas.read_sql_query` to securely fetch data from SQLite and format it into raw CSV string bytes using `.to_csv(index=False)`, avoiding the need to write temporary files to the disk.

### 2. The API Endpoints (`backend/api/reports.py`)
- `GET /reports/executive-summary` -> JSON
- `GET /reports/customer-report` -> CSV String
- `GET /reports/high-risk` -> CSV String
- `GET /reports/segment-summary` -> CSV String

### 3. Frontend Portal (`frontend/pages/Reports.py`)
- Created an intuitive, dark-themed UI providing 1-click downloads.
- **Executive Summary Generation**: Because native Python PDF compilation requires 3rd-party OS dependencies like `fpdf2` (which violate the project's dependency lock), the frontend formats the Executive Summary into a clean, professional `.txt` report string and serves it via `st.download_button`.
- Integrated try/except blocks to gracefully degrade the UI if the FastAPI service is offline, displaying a red "Unavailable" box rather than crashing the application.

## Constraints Addressed
- Retained the exact Streamlit aesthetic.
- Avoided mutating any existing dashboards or prediction centers.
