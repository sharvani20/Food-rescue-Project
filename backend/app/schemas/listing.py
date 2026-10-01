from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.listing import FoodType, ListingStatus
from app.schemas.user import UserOut

class ListingBase(BaseModel):
    title: str
    food_type: FoodType
    quantity_kg: float
    servings: int = 10
    expiry_hours: float = 6.0
    address: str
    latitude: float
    longitude: float
    notes: Optional[str] = None

class ListingCreate(ListingBase):
    pass

class ListingOut(ListingBase):
    id: int
    donor_id: int
    status: ListingStatus
    created_at: datetime
    donor: Optional[UserOut] = None

    class Config:
        from_attributes = True
