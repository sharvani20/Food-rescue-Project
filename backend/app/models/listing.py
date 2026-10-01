from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class FoodType(str, enum.Enum):
    COOKED = "COOKED"          # Cooked meals, catering, buffet
    PERISHABLE = "PERISHABLE"    # Fresh produce, dairy, fruits
    PACKAGED = "PACKAGED"      # Canned goods, packaged snacks
    BAKERY = "BAKERY"          # Bread, pastries, baked items

class ListingStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    MATCHED = "MATCHED"
    CLAIMED = "CLAIMED"
    DELIVERED = "DELIVERED"
    EXPIRED = "EXPIRED"

class FoodListing(Base):
    __tablename__ = "food_listings"

    id = Column(Integer, primary_key=True, index=True)
    donor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    food_type = Column(SQLEnum(FoodType), nullable=False, default=FoodType.COOKED)
    quantity_kg = Column(Float, nullable=False)
    servings = Column(Integer, nullable=False, default=10)
    expiry_hours = Column(Float, nullable=False, default=6.0) # hours remaining
    status = Column(SQLEnum(ListingStatus), nullable=False, default=ListingStatus.AVAILABLE)
    
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    donor = relationship("User", back_populates="listings", foreign_keys=[donor_id])
    matches = relationship("Match", back_populates="listing", cascade="all, delete-orphan")
    deliveries = relationship("Delivery", back_populates="listing")
