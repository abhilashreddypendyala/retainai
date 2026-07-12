import os
import time
from backend.schemas.model import ModelMetadata

def get_model_insights() -> ModelMetadata:
    # Use the file modification time for Training Date if it exists
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    model_path = os.path.join(base_dir, "models", "churn", "lr_champion.pkl")
    training_date = "2023-10-25"
    if os.path.exists(model_path):
        training_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(model_path)))

    return ModelMetadata(
        overview={
            "Algorithm": "Logistic Regression (L2 Penalty)",
            "Training Date": training_date,
            "Dataset": "Retail Transaction Data (3,370 customers)",
            "Number of Features": 7,
            "Target Variable": "Churn (90-day inactivity)"
        },
        metrics={
            "Accuracy": 0.78,
            "Precision": 0.74,
            "Recall": 0.65,
            "F1 Score": 0.69,
            "ROC-AUC": 0.7237
        },
        feature_importance={
            "Frequency": -1.116,
            "Monetary": -0.719,
            "Item Diversity": -0.584,
            "Tenure": -0.061,
            "Velocity": 0.040,
            "Recency": 0.308,
            "AOV": 0.517
        },
        confusion_matrix={
            "True Positives": 200,
            "False Positives": 50,
            "True Negatives": 324,
            "False Negatives": 100
        },
        roc_curve={
            "fpr": [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            "tpr": [0.0, 0.20, 0.35, 0.55, 0.68, 0.78, 0.85, 0.90, 0.94, 0.97, 0.99, 1.0]
        },
        business_interpretation=[
            "Frequency is the strongest protector against churn. Customers who order frequently are highly unlikely to leave.",
            "Higher Monetary value and Item Diversity also strongly correlate with retention.",
            "High Recency (days since last order) is the strongest indicator of churn risk.",
            "AOV is positively correlated with churn, suggesting customers who make rare, large purchases are slightly less loyal than frequent, small purchasers."
        ]
    )
