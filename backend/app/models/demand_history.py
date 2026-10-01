from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from datetime import datetime
from app.core.database import Base

class DemandHistory(Base):
    __tablename__ = "demand_history"

    id = Column(Integer, primary_key=True, index=True)
    ngo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ngo_category = Column(String, nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour_of_day = Column(Integer, nullable=False)  # 0-23
    requested_kg = Column(Float, nullable=False)
    fulfilled_kg = Column(Float, nullable=False)
    capacity_kg = Column(Float, nullable=False)
    is_weekend = Column(Integer, nullable=False, default=0)
    event_factor = Column(Float, nullable=False, default=1.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
