import math
from typing import Tuple, List

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return round(c * r, 2)

def estimate_travel_time_minutes(distance_km: float, avg_speed_kmh: float = 30.0) -> int:
    """
    Estimate travel time in minutes assuming city traffic speed (30 km/h).
    """
    hours = distance_km / max(avg_speed_kmh, 5.0)
    return int(round(hours * 60))

def interpolate_polyline(start: Tuple[float, float], end: Tuple[float, float], num_points: int = 5) -> List[List[float]]:
    """
    Generate intermediate lat/lng coordinates between start and end for smooth route rendering.
    """
    lat1, lon1 = start
    lat2, lon2 = end
    points = []
    for i in range(num_points + 1):
        t = i / float(num_points)
        lat = lat1 + t * (lat2 - lat1)
        lon = lon1 + t * (lon2 - lon1)
        points.append([round(lat, 6), round(lon, 6)])
    return points
