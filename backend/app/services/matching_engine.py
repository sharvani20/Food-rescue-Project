import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.listing import FoodListing, ListingStatus, FoodType
from app.models.ngo_request import NGORequest
from app.models.match import Match
from app.services.geo_utils import haversine_distance, estimate_travel_time_minutes
from app.ml.demand_model import predictor
from app.schemas.match import MatchRecommendation

def rank_ngos_for_listing(db: Session, listing_id: int) -> List[MatchRecommendation]:
    """
    Smart Matching Engine: Ranks candidate NGOs for a posted surplus food listing using:
    - ML predicted demand score
    - Haversine geospatial distance & travel decay
    - NGO storage / distribution capacity
    - Food type compatibility (Cooked, Bakery, Perishable, Packaged)
    - Shelf-life expiry urgency weight
    """
    listing = db.query(FoodListing).filter(FoodListing.id == listing_id).first()
    if not listing:
        return []

    ngos = db.query(User).filter(User.role == UserRole.NGO).all()
    if not ngos:
        return []

    recommendations: List[MatchRecommendation] = []

    for ngo in ngos:
        reasons = []

        # 1. Distance Calculation (Haversine)
        distance_km = haversine_distance(
            listing.latitude, listing.longitude,
            ngo.latitude, ngo.longitude
        )
        
        # Exponential distance decay: S_dist = 100 * exp(-0.12 * distance_km)
        dist_score = max(0.0, min(100.0, 100.0 * math.exp(-0.12 * distance_km)))
        travel_min = estimate_travel_time_minutes(distance_km)
        if distance_km <= 3.0:
            reasons.append(f"📍 Excellent proximity ({distance_km} km, ~{travel_min} mins)")
        elif distance_km <= 10.0:
            reasons.append(f"📍 Nearby location ({distance_km} km)")
        else:
            reasons.append(f"📍 Regional location ({distance_km} km)")

        # 2. ML Predicted Demand Score
        pred_kg, baseline_avg = predictor.predict(db, ngo.id)
        
        # Check explicit NGO requirement requests
        active_req = db.query(NGORequest).filter(
            NGORequest.ngo_id == ngo.id,
            NGORequest.active == True
        ).first()

        effective_demand_kg = pred_kg
        if active_req:
            effective_demand_kg = max(pred_kg, active_req.quantity_needed_kg)
            reasons.append(f"📢 Active NGO Request for {active_req.quantity_needed_kg} kg ({active_req.urgency} urgency)")

        demand_ratio = effective_demand_kg / max(1.0, listing.quantity_kg)
        demand_score = max(10.0, min(100.0, demand_ratio * 75.0))
        reasons.append(f"🤖 ML Forecast: {pred_kg} kg estimated demand")

        # 3. NGO Capacity Score
        ngo_cap = ngo.daily_capacity_kg or 100.0
        if ngo_cap >= listing.quantity_kg:
            capacity_score = 100.0
            reasons.append(f"📦 Capacity match ({ngo_cap} kg max capacity)")
        else:
            capacity_score = max(20.0, round((ngo_cap / listing.quantity_kg) * 100.0, 1))
            reasons.append(f"⚠️ Partial capacity ({ngo_cap} kg vs {listing.quantity_kg} kg needed)")

        # 4. Food Type Compatibility Score
        food_type_match = True
        if active_req and active_req.food_type != listing.food_type:
            food_type_score = 60.0
            food_type_match = False
            reasons.append(f"🍲 Acceptable food category ({listing.food_type.value})")
        else:
            food_type_score = 100.0
            reasons.append(f"✅ Exact food type match ({listing.food_type.value})")

        # 5. Expiry Urgency Score
        # Urgent expiry (< 4h) gives bonus score to close-by NGOs
        if listing.expiry_hours <= 4.0:
            if distance_km <= 5.0:
                expiry_score = 100.0
                reasons.append(f"⏱️ Rapid dispatch ready (Expires in {listing.expiry_hours}h)")
            else:
                expiry_score = 40.0
        else:
            expiry_score = 80.0

        # Composite Weighted Scoring Formula
        composite_score = (
            0.30 * dist_score +
            0.25 * demand_score +
            0.20 * capacity_score +
            0.15 * food_type_score +
            0.10 * expiry_score
        )
        composite_score = round(max(0.0, min(100.0, composite_score)), 1)

        rec = MatchRecommendation(
            ngo_id=ngo.id,
            ngo_name=ngo.name,
            ngo_address=ngo.address or "Address provided upon claim",
            ngo_lat=ngo.latitude,
            ngo_lng=ngo.longitude,
            match_score=composite_score,
            distance_km=distance_km,
            demand_score=round(demand_score, 1),
            expiry_score=round(expiry_score, 1),
            capacity_score=round(capacity_score, 1),
            food_type_match=food_type_match,
            predicted_demand_kg=pred_kg,
            current_demand_kg=effective_demand_kg,
            ngo_capacity_kg=ngo_cap,
            expiry_hours=listing.expiry_hours,
            reasons=reasons
        )
        recommendations.append(rec)

    # Sort descending by match score
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations

def save_top_matches_to_db(db: Session, listing_id: int, top_n: int = 5):
    """
    Persist generated top match scores to database matches table.
    """
    recs = rank_ngos_for_listing(db, listing_id)
    if not recs:
        return

    # Clear existing unaccepted matches for this listing
    db.query(Match).filter(Match.listing_id == listing_id, Match.accepted == False).delete()

    matches_to_add = []
    for rec in recs[:top_n]:
        match = Match(
            listing_id=listing_id,
            ngo_id=rec.ngo_id,
            match_score=rec.match_score,
            distance_km=rec.distance_km,
            demand_score=rec.demand_score,
            expiry_score=rec.expiry_score,
            capacity_score=rec.capacity_score,
            food_type_match=rec.food_type_match,
            accepted=False
        )
        matches_to_add.append(match)

    db.add_all(matches_to_add)
    db.commit()
