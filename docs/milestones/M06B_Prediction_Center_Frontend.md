# Milestone 06B: Prediction Center Frontend

## Objective
Finalize the Prediction Center module by creating an interactive Streamlit page allowing users to generate live churn predictions. The UI must cleanly integrate with the `POST /prediction` endpoint to evaluate both existing database customers and manually entered "what-if" feature sets.

## Architecture & Integration
- **`APIClient` Extension**: `predict_customer()` was added to `api_client.py`. The frontend never reads `.pkl` files directly. It safely delegates all ML inference to the FastAPI backend, preserving the strict 3-tier architecture.
- **Data Hydration for Existing Customers**: When a user selects an existing customer ID, the page internally fetches the `get_customer_360` API, extracts the 7 needed machine learning features (Recency, Frequency, Monetary, Tenure, Velocity, AOV, ItemDiversity) from the raw database profile, and forwards them instantly to the prediction endpoint.
- **Manual Input Mode**: Users can manually tweak any of the 7 features using number input fields to simulate how changes in customer behavior might impact churn probability.

## Components Created/Modified

### 1. `frontend/utils/api_client.py`
- Created `predict_customer` method connecting to `POST /prediction`.

### 2. `frontend/components/prediction_result.py` (NEW)
- A reusable UI function designed to accept a `PredictionResponse` JSON payload and render 4 beautifully styled KPI metric cards displaying Risk Level, Prediction, Probability, and Confidence, alongside a Recommended Action block.

### 3. `frontend/pages/Prediction_Center.py` (NEW)
- **Top Section - Mode Selector**: A radio button allowing the user to select "Existing Customer" (search and dropdown) or "New Customer" (a grid of 7 manual inputs).
- **Middle Section - Inference Grid**: Renders the `prediction_result` component dynamically. Wraps the API call in an `st.spinner()` for a smooth user experience.
- **Bottom Section - History Log**: Maintains a session-state array of the last 10 predictions run, rendering them in the standard `dark_table` format.

## Constraints Addressed
- Maintained the existing Streamlit visual theme.
- Avoided duplicating any feature-parsing or inference logic on the frontend. 
- Gracefully handles backend downtime via `try/except` blocks to prevent ugly tracebacks on the UI.
