from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class DeliveryStatus(str, enum.Enum):
    PENDING = "PENDING"
    MATCHED = "MATCHED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("food_listings.id"), nullable=False)
    ngo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    driver_name = Column(String, nullable=True, default="Volunteer Vehicle #1")
    
    status = Column(SQLEnum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING)
    estimated_distance_km = Column(Float, nullable=True, default=0.0)
    pickup_time = Column(DateTime, nullable=True)
    delivery_time = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    listing = relationship("FoodListing", back_populates="deliveries")
    ngo = relationship("User")
