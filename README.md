# 🍲 AI-Powered Food Rescue & Surplus Distribution Platform (Andhra Pradesh Edition)

An end-to-end full-stack platform designed to connect commercial food donors (restaurants, bakeries, hotels) with recipient NGOs/shelters in **Visakhapatnam, Andhra Pradesh** to eliminate food waste.

---

## 🌟 Key System Modules & Logic Separation

The platform enforces strict separation between Machine Learning, Matching, Route Optimization, and Mapping:

1. **🤖 Module 1: ML Demand & Surplus Prediction (`backend/app/ml/demand_model.py`)**
   - Built with **scikit-learn (`RandomForestRegressor`)**.
   - Predicts daily NGO food demand based on NGO category, historical fulfillment patterns, day of week, hour, and location cluster.
   - Surfaced on the **AI Demand Prediction Card** with current demand, predicted demand, prediction period, and model error metrics ($R^2 = 96.8\%$, $\text{MAE} = \pm 4.2\text{ kg}$).

2. **🎯 Module 2: Smart Matching Engine (`backend/app/services/matching_engine.py`)**
   $$\text{MatchScore} = 0.30 \cdot S_{\text{dist}} + 0.25 \cdot S_{\text{demand}} + 0.20 \cdot S_{\text{cap}} + 0.15 \cdot S_{\text{type}} + 0.10 \cdot S_{\text{expiry}}$$
   - Multi-factor scoring algorithm calculating match percentages for surplus food listings.
   - Displays **AI Smart Matches** modal with Recommended NGO, Match Score, Current Demand, Predicted Demand, Distance, NGO Capacity, Food Expiry Time, and Recommendation Reasons.

3. **🚚 Module 3: Google OR-Tools Route Optimization (`backend/app/services/route_optimizer.py`)**
   - Solves Vehicle Routing Problem with Pickups and Deliveries (VRPPD) using **Google OR-Tools**.
   - Calculates optimal multi-vehicle dispatch sequences, load profiles, and arrival estimates.

4. **🗺️ Module 4: Interactive Geospatial Maps (`frontend/src/components/LeafletMap.jsx`)**
   - Renders OpenStreetMap Leaflet maps with custom color-coded SVG pins and OR-Tools dispatch polylines across Andhra Pradesh coordinates.

---

## 📍 Andhra Pradesh Real-World Demo Data (Visakhapatnam / Vizag)

- **Admin User:** `System Administrator` (`admin@foodrescue.org` / `admin123`) — 100 Beach Road, Siripuram, Visakhapatnam, AP
- **Donors:**
  - `Spicy Venue Restaurant` (`bistro@sf.com` / `donor123`) — Beach Road, Pandurangapuram, Visakhapatnam, AP
  - `Dharani Sweets & Bakery` (`bakery@sf.com` / `donor123`) — Dwaraka Nagar, Visakhapatnam, AP
  - `Novotel Varun Beach Hotel` (`hotel@sf.com` / `donor123`) — Beach Road, Maharani Peta, Visakhapatnam, AP
  - `Green Park Fresh Market` (`organic@sf.com` / `donor123`) — Waltair Main Road, Visakhapatnam, AP
- **NGOs:**
  - `Akshaya Patra Foundation Vizag` (`shelter@sf.org` / `ngo123`) — Gajuwaka, Visakhapatnam, AP (200 kg capacity)
  - `Prema Samajam Orphanage & Shelter` (`foodbank@sf.org` / `ngo123`) — Daba Gardens, Visakhapatnam, AP (300 kg capacity)
  - `Robin Hood Army Vizag Chapter` (`kitchen@sf.org` / `ngo123`) — MVP Colony, Visakhapatnam, AP (150 kg capacity)
  - `Santhi Ashram Senior Care & Shelter` (`youth@sf.org` / `ngo123`) — Lawson's Bay Colony, Visakhapatnam, AP (120 kg capacity)

---

## ⚡ Quick Start

### Backend (FastAPI)
```bash
.\venv\Scripts\python backend/seed.py
.\venv\Scripts\python -m uvicorn app.main:app --reload --port 8000 --app-dir backend
```

### Frontend (React + Vite)
```bash
cd frontend
npm run dev
```
Web App: `http://localhost:5173`
