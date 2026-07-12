# Milestone 06A: Prediction Backend

## Objective
Implement the foundational backend infrastructure for the Prediction Center. This milestone exposes the previously trained Logistic Regression machine learning model via a FastAPI endpoint (`POST /prediction`), allowing users to generate live churn predictions using a custom set of customer features.

## Architecture & Integration
- **Model Loading:** Implemented `backend/ml/model_loader.py` to seamlessly wrap `joblib` and load `models/churn/lr_champion.pkl` and `models/churn/feature_scaler.pkl`. The model is loaded lazily and cached into memory so it isn't repeatedly read from the disk on every request. 
- **Data Pipeline:** Incoming REST features are converted into a `pandas.DataFrame` exactly matching the original training order (`Recency`, `Frequency`, `Monetary`, `Tenure`, `Velocity`, `AOV`, `ItemDiversity`), properly scaled, and passed through the model.
- **Service Layer:** Created `backend/services/prediction_service.py` to compute `confidence_score` and map `churn_probability` to a human-readable `risk_level`.
- **API Router:** Created `backend/api/prediction.py` and successfully registered the new `POST /prediction` router into the main FastAPI application. 

## Components Created

### 1. `backend/schemas/prediction.py`
Defined strict Pydantic schemas:
- `PredictionRequest`: Validates the 7 required numerical features.
- `PredictionResponse`: Standardizes the output to return `churn_probability`, `churn_prediction`, `confidence_score`, and `risk_level`.

### 2. `backend/ml/model_loader.py`
Contains the `ChurnModel` class instance. It executes `joblib.load()` and `.predict_proba()` against the scaled data.

### 3. `backend/services/prediction_service.py`
Connects the Pydantic request to the `ChurnModel` class, computes business metrics, and outputs a structured Pydantic response.
**Risk Level Mapping:**
- 0–30%: Low
- 30–70%: Medium 
- 70–100%: High

### 4. `backend/api/prediction.py`
The dedicated endpoint router.

## Constraints Addressed
- The frontend Streamlit UI was strictly untouched.
- Notebooks were not executed or modified; we utilized the existing `.pkl` artifacts.
- API integrates cleanly into Swagger.
