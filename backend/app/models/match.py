from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("food_listings.id"), nullable=False)
    ngo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    match_score = Column(Float, nullable=False)       # 0 - 100 percentage
    distance_km = Column(Float, nullable=False)
    demand_score = Column(Float, nullable=False)      # 0 - 100
    expiry_score = Column(Float, nullable=False)      # 0 - 100
    capacity_score = Column(Float, nullable=False, default=100.0) # 0 - 100
    food_type_match = Column(Boolean, nullable=False, default=True)
    
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    listing = relationship("FoodListing", back_populates="matches")
    ngo = relationship("User", back_populates="matches")
