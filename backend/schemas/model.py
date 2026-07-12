from pydantic import BaseModel
from typing import List, Dict, Any

class ModelMetadata(BaseModel):
    overview: Dict[str, Any]
    metrics: Dict[str, float]
    feature_importance: Dict[str, float]
    confusion_matrix: Dict[str, int]
    roc_curve: Dict[str, List[float]]
    business_interpretation: List[str]
