from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.listing import FoodListing, ListingStatus
from app.schemas.listing import ListingCreate, ListingOut
from app.services.matching_engine import save_top_matches_to_db

router = APIRouter(prefix="/listings", tags=["Food Listings"])

@router.post("", response_model=ListingOut)
def create_listing(
    listing_in: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.RESTAURANT, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only restaurants/donors can post surplus food listings")

    listing = FoodListing(
        donor_id=current_user.id,
        title=listing_in.title,
        food_type=listing_in.food_type,
        quantity_kg=listing_in.quantity_kg,
        servings=listing_in.servings,
        expiry_hours=listing_in.expiry_hours,
        address=listing_in.address,
        latitude=listing_in.latitude,
        longitude=listing_in.longitude,
        notes=listing_in.notes,
        status=ListingStatus.AVAILABLE
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)

    # Trigger automatic smart matching calculation in background/db
    try:
        save_top_matches_to_db(db, listing.id)
    except Exception as e:
        print(f"Error computing matches on listing create: {e}")

    return listing

@router.get("", response_model=List[ListingOut])
def list_listings(
    status: Optional[ListingStatus] = None,
    donor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(FoodListing)
    if status:
        query = query.filter(FoodListing.status == status)
    if donor_id:
        query = query.filter(FoodListing.donor_id == donor_id)
    
    return query.order_by(FoodListing.created_at.desc()).all()

@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.donor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")

    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted successfully"}
