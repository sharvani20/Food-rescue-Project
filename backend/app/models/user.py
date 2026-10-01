from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base

class UserRole(str, enum.Enum):
    RESTAURANT = "RESTAURANT"
    NGO = "NGO"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.RESTAURANT)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=False, default=17.7231)
    longitude = Column(Float, nullable=False, default=83.3150)
    
    # NGO specific properties
    ngo_category = Column(String, nullable=True) # e.g., Homeless Shelter, Food Bank, Orphanage, Community Kitchen
    daily_capacity_kg = Column(Float, nullable=True, default=100.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    listings = relationship("FoodListing", back_populates="donor", foreign_keys="FoodListing.donor_id")
    ngo_requests = relationship("NGORequest", back_populates="ngo")
    matches = relationship("Match", back_populates="ngo")
