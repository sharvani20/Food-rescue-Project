from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class PredictDemandRequest(BaseModel):
    ngo_id: int
    day_of_week: Optional[int] = None # 0=Monday, 6=Sunday
    hour_of_day: Optional[int] = None # 0-23
    event_factor: Optional[float] = 1.0

class PredictDemandResponse(BaseModel):
    ngo_id: int
    ngo_name: str
    ngo_category: str
    predicted_demand_kg: float
    confidence_interval: List[float] # [lower, upper]
    historical_avg_kg: float
    features_used: Dict[str, Any]

class MLModelMetrics(BaseModel):
    r2_score: float
    mae: float
    rmse: float
    dataset_size: int
    trained_at: str
    model_type: str
