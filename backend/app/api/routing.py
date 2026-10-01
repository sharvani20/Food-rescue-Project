from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.route_optimizer import solve_vrp_routes
from app.schemas.routing import RouteOptimizeResponse

router = APIRouter(prefix="/routing", tags=["Route Optimization (OR-Tools)"])

@router.get("/optimize-routes", response_model=RouteOptimizeResponse)
def optimize_rescue_routes(
    vehicle_capacity_kg: float = Query(150.0, description="Vehicle capacity in kg"),
    num_vehicles: int = Query(2, description="Number of active rescue vehicles"),
    db: Session = Depends(get_db)
):
    """
    Triggers Google OR-Tools Vehicle Routing Problem (VRP) solver.
    Returns optimized pickup & delivery sequences, total travel distances, load profiles,
    and polyline coordinates for Leaflet map display.
    """
    return solve_vrp_routes(db, vehicle_capacity_kg=vehicle_capacity_kg, num_vehicles=num_vehicles)
