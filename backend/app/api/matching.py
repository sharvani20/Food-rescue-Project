from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.listing import FoodListing, ListingStatus
from app.models.match import Match
from app.models.delivery import Delivery, DeliveryStatus
from app.schemas.match import MatchRecommendation
from app.services.matching_engine import rank_ngos_for_listing
from app.services.geo_utils import haversine_distance

router = APIRouter(prefix="/matching", tags=["Smart Matching Engine"])

@router.get("/recommend/{listing_id}", response_model=List[MatchRecommendation])
def get_matching_recommendations(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    return rank_ngos_for_listing(db, listing_id)

@router.post("/claim/{listing_id}")
def claim_donation_match(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.NGO, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only NGOs can claim surplus food matches")

    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != ListingStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail=f"Listing is already {listing.status.value}")

    # Update listing status to MATCHED
    listing.status = ListingStatus.MATCHED

    # Calculate distance
    dist_km = haversine_distance(
        listing.latitude, listing.longitude,
        current_user.latitude, current_user.longitude
    )

    # Create active delivery record with status MATCHED
    delivery = Delivery(
        listing_id=listing.id,
        ngo_id=current_user.id,
        driver_name="Rescue Fleet Vehicle #1",
        status=DeliveryStatus.MATCHED,
        estimated_distance_km=dist_km,
        notes=f"Claimed by {current_user.name}"
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return {
        "message": f"Successfully matched {listing.title} with {current_user.name}",
        "delivery_id": delivery.id,
        "status": delivery.status.value
    }
