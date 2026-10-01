from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.delivery import Delivery, DeliveryStatus
from app.models.listing import FoodListing, ListingStatus
from app.schemas.delivery import DeliveryOut, DeliveryStatusUpdate

router = APIRouter(prefix="/deliveries", tags=["Delivery Workflow"])

@router.get("", response_model=List[DeliveryOut])
def list_deliveries(
    status: Optional[DeliveryStatus] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    return query.order_by(Delivery.created_at.desc()).all()

@router.patch("/{delivery_id}/status", response_model=DeliveryOut)
def update_delivery_status(
    delivery_id: int,
    status_update: DeliveryStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")

    new_status = status_update.status
    delivery.status = new_status
    if status_update.notes:
        delivery.notes = status_update.notes

    if new_status == DeliveryStatus.PICKED_UP:
        delivery.pickup_time = datetime.utcnow()
    elif new_status == DeliveryStatus.DELIVERED:
        delivery.delivery_time = datetime.utcnow()
        # Update associated listing status to DELIVERED
        if delivery.listing:
            delivery.listing.status = ListingStatus.DELIVERED

    db.commit()
    db.refresh(delivery)
    return delivery
