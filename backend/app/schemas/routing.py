from pydantic import BaseModel
from typing import List, Optional

class RouteStop(BaseModel):
    step_number: int
    location_name: str
    type: str  # "DEPOT", "PICKUP", "DELIVERY"
    latitude: float
    longitude: float
    address: str
    item_title: Optional[str] = None
    quantity_kg: Optional[float] = None
    arrival_time_est: Optional[str] = None

class VehicleRoute(BaseModel):
    vehicle_id: int
    driver_name: str
    stops: List[RouteStop]
    total_distance_km: float
    total_load_kg: float
    polyline_coords: List[List[float]] # [[lat, lng], [lat, lng], ...]

class RouteOptimizeResponse(BaseModel):
    status: str
    num_vehicles_used: int
    total_distance_km: float
    total_food_delivered_kg: float
    routes: List[VehicleRoute]
