from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.listing import FoodType
from app.models.ngo_request import UrgencyLevel
from app.schemas.user import UserOut

class NGORequestBase(BaseModel):
    food_type: FoodType
    quantity_needed_kg: float
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    active: bool = True

class NGORequestCreate(NGORequestBase):
    pass

class NGORequestOut(NGORequestBase):
    id: int
    ngo_id: int
    created_at: datetime
    ngo: Optional[UserOut] = None

    class Config:
        from_attributes = True
