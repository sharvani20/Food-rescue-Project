from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from app.models.listing import FoodListing, ListingStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.models.user import User, UserRole
from app.services.geo_utils import haversine_distance, estimate_travel_time_minutes, interpolate_polyline
from app.schemas.routing import RouteOptimizeResponse, VehicleRoute, RouteStop

def solve_vrp_routes(db: Session, vehicle_capacity_kg: float = 150.0, num_vehicles: int = 2) -> RouteOptimizeResponse:
    """
    Solves Vehicle Routing Problem with Pickups and Deliveries (VRPPD) using Google OR-Tools.
    Optimizes multi-stop routes for rescue vehicles connecting donors to recipient NGOs.
    """
    # Fetch active matched or pending deliveries/listings
    deliveries = db.query(Delivery).filter(
        Delivery.status.in_([DeliveryStatus.PENDING, DeliveryStatus.MATCHED])
    ).all()

    # If no active deliveries in DB, synthesize active pairs from available listings for demo route planning
    nodes_info = []
    depot_coords = (17.7231, 83.3150) # Central depot (Visakhapatnam, Andhra Pradesh)
    depot_name = "Central Food Rescue Hub Vizag"

    # Node 0 is always Depot
    nodes_info.append({
        "type": "DEPOT",
        "id": 0,
        "name": depot_name,
        "lat": depot_coords[0],
        "lng": depot_coords[1],
        "demand": 0,
        "address": "100 Beach Road, Siripuram, Visakhapatnam, AP",
        "listing": None
    })

    node_counter = 1
    pickup_delivery_pairs = []

    if deliveries:
        for deliv in deliveries:
            listing = deliv.listing
            ngo = deliv.ngo
            if not listing or not ngo:
                continue

            pickup_node = node_counter
            nodes_info.append({
                "type": "PICKUP",
                "id": pickup_node,
                "name": f"Pickup: {listing.title}",
                "lat": listing.latitude,
                "lng": listing.longitude,
                "demand": int(listing.quantity_kg),
                "address": listing.address,
                "listing_title": listing.title,
                "quantity_kg": listing.quantity_kg
            })
            node_counter += 1

            delivery_node = node_counter
            nodes_info.append({
                "type": "DELIVERY",
                "id": delivery_node,
                "name": f"Delivery: {ngo.name}",
                "lat": ngo.latitude,
                "lng": ngo.longitude,
                "demand": -int(listing.quantity_kg),
                "address": ngo.address or "NGO Center",
                "listing_title": listing.title,
                "quantity_kg": listing.quantity_kg
            })
            node_counter += 1

            pickup_delivery_pairs.append((pickup_node, delivery_node))
    else:
        # Fallback to available listings matching NGOs
        listings = db.query(FoodListing).filter(
            FoodListing.status.in_([ListingStatus.AVAILABLE, ListingStatus.MATCHED])
        ).limit(6).all()
        ngos = db.query(User).filter(User.role == UserRole.NGO).limit(4).all()

        if listings and ngos:
            depot_coords = (listings[0].latitude, listings[0].longitude)
            nodes_info[0]["lat"] = depot_coords[0]
            nodes_info[0]["lng"] = depot_coords[1]

            for i, listing in enumerate(listings):
                ngo = ngos[i % len(ngos)]
                
                p_node = node_counter
                nodes_info.append({
                    "type": "PICKUP",
                    "id": p_node,
                    "name": f"Pickup: {listing.title}",
                    "lat": listing.latitude,
                    "lng": listing.longitude,
                    "demand": int(listing.quantity_kg),
                    "address": listing.address,
                    "listing_title": listing.title,
                    "quantity_kg": listing.quantity_kg
                })
                node_counter += 1

                d_node = node_counter
                nodes_info.append({
                    "type": "DELIVERY",
                    "id": d_node,
                    "name": f"Delivery: {ngo.name}",
                    "lat": ngo.latitude,
                    "lng": ngo.longitude,
                    "demand": -int(listing.quantity_kg),
                    "address": ngo.address or "NGO Center",
                    "listing_title": listing.title,
                    "quantity_kg": listing.quantity_kg
                })
                node_counter += 1

                pickup_delivery_pairs.append((p_node, d_node))

    num_locations = len(nodes_info)
    if num_locations <= 1:
        return RouteOptimizeResponse(
            status="No active food rescues available to route.",
            num_vehicles_used=0,
            total_distance_km=0.0,
            total_food_delivered_kg=0.0,
            routes=[]
        )

    # 1. Build Distance Matrix (in meters)
    distance_matrix = []
    for i in range(num_locations):
        row = []
        for j in range(num_locations):
            if i == j:
                row.append(0)
            else:
                dist_km = haversine_distance(
                    nodes_info[i]["lat"], nodes_info[i]["lng"],
                    nodes_info[j]["lat"], nodes_info[j]["lng"]
                )
                row.append(int(dist_km * 1000)) # convert to meters
        distance_matrix.append(row)

    # 2. OR-Tools Routing Index Manager & Routing Model
    manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Distance Cost Callback
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Distance Dimension for travel accumulation and pickup-before-delivery order
    routing.AddDimension(
        transit_callback_index,
        0,  # no slack
        300000,  # max distance per vehicle in meters (300 km)
        True,  # start at 0
        "Distance"
    )
    distance_dimension = routing.GetDimensionOrDie("Distance")

    # Demand / Capacity Dimension
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return nodes_info[from_node]["demand"]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        [int(vehicle_capacity_kg)] * num_vehicles,  # vehicle capacities
        True,  # start load at zero
        "Capacity"
    )

    # Pickup and Delivery constraints
    for pickup_idx, delivery_idx in pickup_delivery_pairs:
        p_index = manager.NodeToIndex(pickup_idx)
        d_index = manager.NodeToIndex(delivery_idx)
        routing.AddPickupAndDelivery(p_index, d_index)
        routing.solver().Add(
            routing.VehicleVar(p_index) == routing.VehicleVar(d_index)
        )
        routing.solver().Add(
            distance_dimension.CumulVar(p_index) <= distance_dimension.CumulVar(d_index)
        )

    # Search parameters
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    )

    # Solve VRP problem
    solution = routing.SolveWithParameters(search_parameters)

    if not solution:
        # Fallback to direct routing if tight constraints
        return RouteOptimizeResponse(
            status="No feasible OR-Tools solution under tight capacity constraints.",
            num_vehicles_used=0,
            total_distance_km=0.0,
            total_food_delivered_kg=0.0,
            routes=[]
        )

    # Construct formatted result
    vehicle_routes: List[VehicleRoute] = []
    total_distance_meters = 0
    total_food_delivered_kg = 0.0

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        stops: List[RouteStop] = []
        polyline_coords: List[List[float]] = []
        route_dist_meters = 0
        current_load = 0
        step_number = 1

        prev_node_coords = None

        while not routing.IsEnd(index):
            node_idx = manager.IndexToNode(index)
            info = nodes_info[node_idx]

            current_coords = (info["lat"], info["lng"])
            if prev_node_coords:
                # Add interpolated points between stops for map polyline
                interp = interpolate_polyline(prev_node_coords, current_coords, num_points=6)
                polyline_coords.extend(interp)
            else:
                polyline_coords.append([info["lat"], info["lng"]])

            prev_node_coords = current_coords

            current_load += info["demand"]
            if info["type"] == "PICKUP":
                total_food_delivered_kg += info.get("quantity_kg", 0)

            est_time = f"+{estimate_travel_time_minutes(route_dist_meters / 1000.0)} mins"

            stops.append(RouteStop(
                step_number=step_number,
                location_name=info["name"],
                type=info["type"],
                latitude=info["lat"],
                longitude=info["lng"],
                address=info["address"],
                item_title=info.get("listing_title"),
                quantity_kg=info.get("quantity_kg"),
                arrival_time_est=est_time
            ))

            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_dist_meters += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

        # Add final return to depot
        end_node_idx = manager.IndexToNode(index)
        end_info = nodes_info[end_node_idx]
        if prev_node_coords:
            interp = interpolate_polyline(prev_node_coords, (end_info["lat"], end_info["lng"]), num_points=6)
            polyline_coords.extend(interp)

        stops.append(RouteStop(
            step_number=step_number + 1,
            location_name=f"Return to {end_info['name']}",
            type="DEPOT",
            latitude=end_info["lat"],
            longitude=end_info["lng"],
            address=end_info["address"],
            arrival_time_est=f"+{estimate_travel_time_minutes(route_dist_meters / 1000.0)} mins"
        ))

        route_km = round(route_dist_meters / 1000.0, 2)
        total_distance_meters += route_dist_meters

        if len(stops) > 2: # Has actual pickups/deliveries
            vehicle_routes.append(VehicleRoute(
                vehicle_id=vehicle_id + 1,
                driver_name=f"Rescue Van #{vehicle_id + 1}",
                stops=stops,
                total_distance_km=route_km,
                total_load_kg=float(max(0, current_load)),
                polyline_coords=polyline_coords
            ))

    total_km = round(total_distance_meters / 1000.0, 2)

    return RouteOptimizeResponse(
        status="OR-Tools Route Optimization Completed Successfully",
        num_vehicles_used=len(vehicle_routes),
        total_distance_km=total_km,
        total_food_delivered_kg=round(total_food_delivered_kg, 1),
        routes=vehicle_routes
    )
