from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user import UserOut
from app.schemas.listing import ListingOut

class MatchOut(BaseModel):
    id: int
    listing_id: int
    ngo_id: int
    match_score: float
    distance_km: float
    demand_score: float
    expiry_score: float
    capacity_score: float
    food_type_match: bool
    accepted: bool
    created_at: datetime
    ngo: Optional[UserOut] = None
    listing: Optional[ListingOut] = None

    class Config:
        from_attributes = True

class MatchRecommendation(BaseModel):
    ngo_id: int
    ngo_name: str
    ngo_address: str
    ngo_lat: float
    ngo_lng: float
    match_score: float
    distance_km: float
    demand_score: float
    expiry_score: float
    capacity_score: float
    food_type_match: bool
    predicted_demand_kg: float
    current_demand_kg: float
    ngo_capacity_kg: float
    expiry_hours: float
    reasons: list[str]
