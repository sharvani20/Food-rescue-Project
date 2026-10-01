from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from app.core.database import Base
from app.models.listing import FoodType

class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class NGORequest(Base):
    __tablename__ = "ngo_requests"

    id = Column(Integer, primary_key=True, index=True)
    ngo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_type = Column(SQLEnum(FoodType), nullable=False, default=FoodType.COOKED)
    quantity_needed_kg = Column(Float, nullable=False)
    urgency = Column(SQLEnum(UrgencyLevel), nullable=False, default=UrgencyLevel.MEDIUM)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    ngo = relationship("User", back_populates="ngo_requests")
