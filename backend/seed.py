import sys
import os
from datetime import datetime, timedelta

# Ensure backend folder is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.listing import FoodListing, FoodType, ListingStatus
from app.models.ngo_request import NGORequest, UrgencyLevel
from app.models.delivery import Delivery, DeliveryStatus
from app.ml.demand_model import predictor, seed_synthetic_demand_history
from app.services.matching_engine import save_top_matches_to_db

def seed_database():
    print("[INIT] Re-creating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("[USERS] Creating demo users (Admin, Donors, NGOs in Andhra Pradesh)...")

        # 1. Admin User
        admin = User(
            email="admin@foodrescue.org",
            hashed_password=get_password_hash("admin123"),
            name="System Administrator",
            role=UserRole.ADMIN,
            phone="+91 891 2550100",
            address="100 Beach Road, Siripuram, Visakhapatnam, Andhra Pradesh 530003",
            latitude=17.7231,
            longitude=83.3150
        )
        db.add(admin)

        # 2. Restaurant Donors (Visakhapatnam, Andhra Pradesh)
        donors = [
            User(
                email="bistro@sf.com",
                hashed_password=get_password_hash("donor123"),
                name="Spicy Venue Restaurant",
                role=UserRole.RESTAURANT,
                phone="+91 891 2701120",
                address="Beach Road, Pandurangapuram, Visakhapatnam, AP 530003",
                latitude=17.7135,
                longitude=83.3228
            ),
            User(
                email="bakery@sf.com",
                hashed_password=get_password_hash("donor123"),
                name="Dharani Sweets & Bakery",
                role=UserRole.RESTAURANT,
                phone="+91 891 2541133",
                address="Dwaraka Nagar 2nd Lane, Visakhapatnam, AP 530016",
                latitude=17.7270,
                longitude=83.3085
            ),
            User(
                email="hotel@sf.com",
                hashed_password=get_password_hash("donor123"),
                name="Novotel Varun Beach Hotel",
                role=UserRole.RESTAURANT,
                phone="+91 891 3041144",
                address="Beach Road, Maharani Peta, Visakhapatnam, AP 530002",
                latitude=17.7088,
                longitude=83.3134
            ),
            User(
                email="organic@sf.com",
                hashed_password=get_password_hash("donor123"),
                name="Green Park Fresh Market",
                role=UserRole.RESTAURANT,
                phone="+91 891 2561155",
                address="Waltair Main Road, Visakhapatnam, AP 530002",
                latitude=17.7245,
                longitude=83.3120
            )
        ]
        db.add_all(donors)

        # 3. Recipient NGOs (Visakhapatnam, Andhra Pradesh)
        ngos = [
            User(
                email="shelter@sf.org",
                hashed_password=get_password_hash("ngo123"),
                name="Akshaya Patra Foundation Vizag",
                role=UserRole.NGO,
                phone="+91 891 2780211",
                address="Resapuvanipalem, Visakhapatnam, AP 530013",
                latitude=17.7180,
                longitude=83.3180,
                ngo_category="Homeless Shelter",
                daily_capacity_kg=200.0
            ),
            User(
                email="foodbank@sf.org",
                hashed_password=get_password_hash("ngo123"),
                name="Prema Samajam Orphanage & Shelter",
                role=UserRole.NGO,
                phone="+91 891 2560222",
                address="Daba Gardens, Visakhapatnam, AP 530020",
                latitude=17.7120,
                longitude=83.3000,
                ngo_category="Food Bank",
                daily_capacity_kg=300.0
            ),
            User(
                email="kitchen@sf.org",
                hashed_password=get_password_hash("ngo123"),
                name="Robin Hood Army Vizag Chapter",
                role=UserRole.NGO,
                phone="+91 891 2530233",
                address="MVP Colony Sector 4, Visakhapatnam, AP 530017",
                latitude=17.7390,
                longitude=83.3320,
                ngo_category="Community Kitchen",
                daily_capacity_kg=150.0
            ),
            User(
                email="youth@sf.org",
                hashed_password=get_password_hash("ngo123"),
                name="Santhi Ashram Senior Care & Shelter",
                role=UserRole.NGO,
                phone="+91 891 2540244",
                address="Lawson's Bay Colony, Visakhapatnam, AP 530017",
                latitude=17.7300,
                longitude=83.3380,
                ngo_category="Orphanage & Youth Shelter",
                daily_capacity_kg=120.0
            )
        ]
        db.add_all(ngos)
        db.commit()

        # Refresh donor & ngo objects
        donor1 = donors[0]
        donor2 = donors[1]
        donor3 = donors[2]
        donor4 = donors[3]

        ngo1 = ngos[0]
        ngo2 = ngos[1]

        print("[LISTINGS] Creating surplus food listings...")
        listings = [
            FoodListing(
                donor_id=donor1.id,
                title="Fresh Biryani & Veg Curry Meals",
                food_type=FoodType.COOKED,
                quantity_kg=45.0,
                servings=90,
                expiry_hours=3.5,
                address=donor1.address,
                latitude=donor1.latitude,
                longitude=donor1.longitude,
                notes="Prepared for lunch buffet. Kept in thermal insulated food-grade containers.",
                status=ListingStatus.AVAILABLE
            ),
            FoodListing(
                donor_id=donor2.id,
                title="Fresh Chapati, Naan & Sweets Assortment",
                food_type=FoodType.BAKERY,
                quantity_kg=25.0,
                servings=70,
                expiry_hours=12.0,
                address=donor2.address,
                latitude=donor2.latitude,
                longitude=donor2.longitude,
                notes="Baked fresh this morning. Sealed in hygenic food boxes.",
                status=ListingStatus.AVAILABLE
            ),
            FoodListing(
                donor_id=donor3.id,
                title="South Indian Thali Meals & Rice Dishes",
                food_type=FoodType.COOKED,
                quantity_kg=60.0,
                servings=120,
                expiry_hours=5.0,
                address=donor3.address,
                latitude=donor3.latitude,
                longitude=donor3.longitude,
                notes="Surplus from afternoon wedding catering function.",
                status=ListingStatus.MATCHED
            ),
            FoodListing(
                donor_id=donor4.id,
                title="Fresh Organic Apples, Mangoes & Vegetables",
                food_type=FoodType.PERISHABLE,
                quantity_kg=55.0,
                servings=110,
                expiry_hours=24.0,
                address=donor4.address,
                latitude=donor4.latitude,
                longitude=donor4.longitude,
                notes="Fresh wholesome produce surplus from market stock.",
                status=ListingStatus.DELIVERED
            ),
        ]
        db.add_all(listings)
        db.commit()

        print("[REQUESTS] Creating active NGO requirement requests...")
        ngo_reqs = [
            NGORequest(
                ngo_id=ngo1.id,
                food_type=FoodType.COOKED,
                quantity_needed_kg=50.0,
                urgency=UrgencyLevel.HIGH,
                active=True
            ),
            NGORequest(
                ngo_id=ngos[2].id,
                food_type=FoodType.COOKED,
                quantity_needed_kg=40.0,
                urgency=UrgencyLevel.CRITICAL,
                active=True
            ),
            NGORequest(
                ngo_id=ngo2.id,
                food_type=FoodType.PERISHABLE,
                quantity_needed_kg=100.0,
                urgency=UrgencyLevel.MEDIUM,
                active=True
            )
        ]
        db.add_all(ngo_reqs)
        db.commit()

        print("[DELIVERIES] Creating initial active delivery tracking records...")
        deliveries = [
            Delivery(
                listing_id=listings[2].id, # South Indian Thali Meals
                ngo_id=ngo1.id,
                driver_name="Vizag Rescue Van #1",
                status=DeliveryStatus.MATCHED,
                estimated_distance_km=2.4,
                notes="Dispatch confirmed for pickup at 4:30 PM."
            ),
            Delivery(
                listing_id=listings[3].id, # Organic Fruits & Veggies
                ngo_id=ngo2.id,
                driver_name="Vizag Rescue Van #2",
                status=DeliveryStatus.DELIVERED,
                estimated_distance_km=3.8,
                pickup_time=datetime.utcnow() - timedelta(hours=3),
                delivery_time=datetime.utcnow() - timedelta(hours=2),
                notes="Successfully delivered and signed by shelter manager."
            )
        ]
        db.add_all(deliveries)
        db.commit()

        print("[ML] Training ML demand prediction model on historical dataset...")
        seed_synthetic_demand_history(db)
        predictor.train(db)

        print("[MATCHING] Computing smart match scores for listings...")
        for listing in listings:
            save_top_matches_to_db(db, listing.id)

        print("[SUCCESS] Database seed completed successfully!")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
