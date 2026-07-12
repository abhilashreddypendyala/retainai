# Milestone 07: Explainable AI & Model Insights

## Objective
Implement an Explainable AI module targeted at technical stakeholders (data scientists, engineers, and leadership) to provide deep visibility into the performance, internal mechanics, and business logic of the Logistic Regression model driving RetainAI's churn predictions.

## Architecture & Integration
- **Zero Retraining Guarantee**: The system reads the live parameters directly from the trained Python artifact (`lr_champion.pkl`) that is already in production. No notebooks are re-run, ensuring parity with the Prediction Center outputs.
- **REST Abstraction**: A new `GET /model/insights` endpoint cleanly proxies the model metadata through FastAPI, so the Streamlit frontend remains completely isolated from the raw `joblib` artifacts.
- **Visual Interpretability**: Leveraged `plotly` to build interactive, responsive visualizations explaining feature weights, decision boundaries, and accuracy metrics.

## Components Created

### 1. Backend Service (`backend/services/model_service.py`)
- Programmatically extracts the true `coef_` array mapped to the 7 features: Recency, Frequency, Monetary, Tenure, Velocity, AOV, and ItemDiversity.
- Formats ROC-AUC curve coordinates, Confusion Matrix counts, and overall metrics (Accuracy, Precision, Recall, F1 Score).
- Synthesizes coefficient weights into human-readable `business_interpretation` bullet points.

### 2. Schemas & API (`backend/schemas/model.py`, `backend/api/model.py`)
- Designed rigorous Pydantic schemas (`ModelMetadata`) encompassing nested dictionaries for `overview`, `metrics`, `feature_importance`, `confusion_matrix`, and `roc_curve`.
- Registered `model_router` cleanly in `main.py`.

### 3. Frontend App (`frontend/pages/Model_Insights.py`)
Added a new interactive Streamlit page displaying:
- **Model Overview**: A top-line breakdown of the algorithm architecture (L2 Penalty) and dataset size.
- **Validation**: Four KPI `metric_cards` showcasing the testing metrics.
- **ROC Curve**: A `px.line` chart mapping True Positive Rate against False Positive Rate.
- **Confusion Matrix**: A `go.Heatmap` vividly breaking down True/False Positives/Negatives using a modern color palette.
- **Relative Feature Importance**: A horizontal bar chart parsing the coefficient weights. Bars are colored intuitively: green blocks churn (e.g. Frequency), red drives churn (e.g. Recency).

## Constraints Addressed
- Strict adherence to reusing the previously trained assets without modifying any notebook logic.
- Maintained the dark aesthetic theme consistent across the Dashboard and Customer Intelligence modules.
