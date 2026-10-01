from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.delivery import DeliveryStatus
from app.schemas.user import UserOut
from app.schemas.listing import ListingOut

class DeliveryCreate(BaseModel):
    listing_id: int
    ngo_id: int
    driver_name: Optional[str] = "Volunteer Vehicle #1"
    notes: Optional[str] = None

class DeliveryStatusUpdate(BaseModel):
    status: DeliveryStatus
    notes: Optional[str] = None

class DeliveryOut(BaseModel):
    id: int
    listing_id: int
    ngo_id: int
    driver_name: Optional[str]
    status: DeliveryStatus
    estimated_distance_km: Optional[float]
    pickup_time: Optional[datetime]
    delivery_time: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    listing: Optional[ListingOut] = None
    ngo: Optional[UserOut] = None

    class Config:
        from_attributes = True
