# Milestone 05C: Customer 360

## Objective
Finalize the Customer Intelligence module by implementing the "Customer 360" profile. This feature allows users to select a customer directly from the explorer table and view their complete business, risk, transaction, and recommendation profile on the same page.

## Architecture & Integration
- **Zero New API Routes**: To preserve simplicity and architectural rules, the `GET /customers/{customer_id}` endpoint was enhanced to return all required 360-degree data (profile, recent transactions, and deterministic recommendations) in a single unified JSON response.
- **Frontend Placement**: The Customer 360 viewer is injected dynamically at the bottom of `frontend/pages/Customer_Intelligence.py` when a user selects an ID from the dropdown, adhering strictly to the "do not create additional pages" constraint.

## Components Modified

### 1. Backend Schemas (`backend/schemas/customer.py`)
- Added `TransactionItem` for structured transaction history typing.
- Added `Recommendation` for structured business actions.
- Added `Customer360Response` to serve as the new master response model for the single-customer endpoint.

### 2. Service Layer (`backend/services/customer_service.py`)
- Enhanced `get_customer_by_id`:
  - Fetches the base profile.
  - Queries `SELECT * FROM transactions WHERE customer_id = ? ORDER BY date DESC LIMIT 10` for recent purchases.
  - Passes the profile through a new `_generate_recommendation()` deterministic logic block.
- **Recommendation Logic**: Evaluates `churn_prediction` and `clv` to categorize the required action:
  - High CLV + High Risk = Win-Back Campaign (VIP)
  - Avg CLV + High Risk = Discount Offer (15%)
  - High CLV + Low Risk = Loyalty Program / Upsell
  - Avg CLV + Low Risk = Standard Marketing Drip

### 3. API Client & Frontend UI (`frontend/utils/api_client.py` & `frontend/pages/Customer_Intelligence.py`)
- Mapped `api_client.get_customer_360(id)` to the endpoint.
- **UI Flow**: 
  - Once a search/filter executes, the user sees a "Deep Dive" section below the table.
  - A form wraps a `selectbox` populated *only* with the customer IDs currently visible in the table.
  - Clicking "View Customer 360" expands the profile dynamically below the form.
- **Visuals**: Reused `metric_card` and `dark_table` for consistent Dashboard-level aesthetics. Added 9 KPI cards for Business Metrics and Risk Analysis, alongside a custom table for recent purchases and an AI Reasoning box.

## Constraints Addressed
- No LLMs were called; logic is entirely deterministic based on customer parameters.
- Maintains the existing Streamlit visual theme.
- Avoided adding new pages or modifying the database schemas.
