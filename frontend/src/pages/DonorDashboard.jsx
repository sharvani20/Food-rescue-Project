import React, { useState, useEffect } from 'react';
import { listingsAPI, matchingAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { LeafletMap } from '../components/LeafletMap';
import { MatchScoreBadge } from '../components/MatchScoreBadge';
import { Utensils, Plus, Sparkles, MapPin, Clock, Trash2, CheckCircle2, X } from 'lucide-react';

export const DonorDashboard = () => {
  const { user } = useAuth();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  // New Listing Form State
  const [form, setForm] = useState({
    title: 'Fresh Biryani & Veg Curry Meals',
    food_type: 'COOKED',
    quantity_kg: 35,
    servings: 70,
    expiry_hours: 4.5,
    address: user?.address || 'Beach Road, Pandurangapuram, Visakhapatnam, AP 530003',
    latitude: user?.latitude || 17.7135,
    longitude: user?.longitude || 83.3228,
    notes: 'Includes steamed basmati rice, paneer butter masala, and mixed veg curries.'
  });

  // Matching Engine Modal State
  const [selectedListing, setSelectedListing] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecs, setLoadingRecs] = useState(false);

  useEffect(() => {
    fetchListings();
  }, [user]);

  const fetchListings = async () => {
    try {
      setLoading(true);
      const res = await listingsAPI.getListings();
      setListings(res.data);
    } catch (err) {
      console.error("Error loading listings", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      await listingsAPI.createListing(form);
      fetchListings();
      alert("✅ Surplus food listing posted successfully! AI matching engine initiated.");
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to post listing.");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this listing?")) return;
    try {
      await listingsAPI.deleteListing(id);
      fetchListings();
    } catch (err) {
      alert("Could not delete listing.");
    }
  };

  const handleViewMatches = async (listing) => {
    setSelectedListing(listing);
    setLoadingRecs(true);
    try {
      const res = await matchingAPI.getRecommendations(listing.id);
      setRecommendations(res.data);
    } catch (err) {
      console.error("Error loading recommendations", err);
    } finally {
      setLoadingRecs(false);
    }
  };

  // Prepare map pins for donor's listings
  const mapMarkers = listings.map((l) => ({
    id: l.id,
    lat: l.latitude,
    lng: l.longitude,
    title: l.title,
    type: 'DONOR',
    address: l.address,
    notes: `${l.quantity_kg} kg • ${l.status}`
  }));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Restaurant & Donor Dashboard</h1>
          <p style={{ color: 'var(--text-muted)' }}>Post surplus food, track pickups, and run AI smart matching engine.</p>
        </div>
        <div style={{ background: '#ecfdf5', color: '#059669', padding: '8px 16px', borderRadius: '20px', fontWeight: 700, fontSize: '0.85rem' }}>
          {user?.name} · Donor
        </div>
      </div>

      <div className="grid-2">
        {/* Post Food Form */}
        <div className="card">
          <div className="card-title">
            <Plus size={20} color="#059669" />
            <span>Post New Surplus Food</span>
          </div>

          <form onSubmit={handleCreate}>
            <div className="form-group">
              <label className="form-label">Food Title / Description</label>
              <input
                type="text"
                className="form-control"
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                required
              />
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Food Category</label>
                <select
                  className="form-control"
                  value={form.food_type}
                  onChange={(e) => setForm({ ...form, food_type: e.target.value })}
                >
                  <option value="COOKED">Cooked Meals / Buffet</option>
                  <option value="BAKERY">Fresh Bakery & Bread</option>
                  <option value="PERISHABLE">Produce & Dairy</option>
                  <option value="PACKAGED">Packaged & Canned Goods</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Quantity (kg)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-control"
                  value={form.quantity_kg}
                  onChange={(e) => setForm({ ...form, quantity_kg: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>

            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Est. Servings</label>
                <input
                  type="number"
                  className="form-control"
                  value={form.servings}
                  onChange={(e) => setForm({ ...form, servings: parseInt(e.target.value) })}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Shelf-Life Expiry (Hours)</label>
                <input
                  type="number"
                  step="0.5"
                  className="form-control"
                  value={form.expiry_hours}
                  onChange={(e) => setForm({ ...form, expiry_hours: parseFloat(e.target.value) })}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Pickup Address</label>
              <input
                type="text"
                className="form-control"
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Packaging & Handling Notes</label>
              <textarea
                className="form-control"
                rows="2"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
              ></textarea>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={creating}>
              {creating ? 'Posting Surplus...' : 'Post Surplus Food Listing'}
            </button>
          </form>
        </div>

        {/* Map View */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card-title">
            <MapPin size={20} color="#2563eb" />
            <span>Active Donor Locations Map (Andhra Pradesh)</span>
          </div>
          <LeafletMap markers={mapMarkers} height="400px" />
        </div>
      </div>

      {/* Active Listings Table */}
      <div className="card">
        <div className="card-title" style={{ justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Utensils size={20} color="#059669" />
            <span>Active Surplus Food Listings ({listings.length})</span>
          </div>
        </div>

        {loading ? (
          <p style={{ color: 'var(--text-muted)' }}>Loading listings...</p>
        ) : listings.length === 0 ? (
          <p style={{ color: 'var(--text-muted)' }}>No active surplus food postings yet.</p>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Title & Category</th>
                  <th>Quantity</th>
                  <th>Expiry Window</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {listings.map((l) => (
                  <tr key={l.id}>
                    <td>
                      <strong style={{ color: 'var(--text-main)' }}>{l.title}</strong>
                      <br />
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{l.food_type} • {l.address}</span>
                    </td>
                    <td>
                      <strong>{l.quantity_kg} kg</strong>
                      <br />
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>~{l.servings} servings</span>
                    </td>
                    <td>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                        <Clock size={14} color="#d97706" />
                        <span>{l.expiry_hours} hours remaining</span>
                      </span>
                    </td>
                    <td>
                      <span className={`badge status-${l.status}`}>{l.status}</span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                          className="btn btn-accent btn-sm"
                          onClick={() => handleViewMatches(l)}
                        >
                          <Sparkles size={14} />
                          AI Smart Matches
                        </button>
                        <button
                          className="btn btn-outline btn-sm"
                          onClick={() => handleDelete(l.id)}
                          style={{ color: '#dc2626' }}
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Smart Matching Recommendations Modal */}
      {selectedListing && (
        <div className="modal-overlay">
          <div className="modal-card" style={{ maxWidth: '720px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Sparkles size={20} color="#4f46e5" />
                  AI Matching Engine Recommendations
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Listing: <strong>{selectedListing.title}</strong> ({selectedListing.quantity_kg} kg, {selectedListing.food_type})
                </p>
              </div>
              <button onClick={() => setSelectedListing(null)} className="btn btn-outline btn-sm">
                <X size={18} />
              </button>
            </div>

            {loadingRecs ? (
              <p style={{ color: 'var(--text-muted)', padding: '20px 0' }}>Computing multi-factor matching scores...</p>
            ) : recommendations.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No candidate NGOs found nearby.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {recommendations.map((rec, index) => (
                  <div
                    key={rec.ngo_id}
                    style={{
                      border: '1px solid var(--border)',
                      borderRadius: '12px',
                      padding: '16px',
                      background: index === 0 ? '#f0fdf4' : '#ffffff',
                      borderColor: index === 0 ? '#86efac' : 'var(--border)'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                      <div>
                        <strong style={{ fontSize: '1.1rem', color: '#0f172a' }}>{rec.ngo_name}</strong>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{rec.ngo_address}</div>
                      </div>
                      <MatchScoreBadge score={rec.match_score} />
                    </div>

                    {/* Informative AI Metrics Breakdown Grid */}
                    <div className="grid-3" style={{ background: '#f8fafc', border: '1px solid var(--border)', padding: '10px', borderRadius: '8px', fontSize: '0.82rem', marginBottom: '12px', gap: '8px' }}>
                      <div>📢 <strong>Current Demand:</strong> {rec.current_demand_kg ? `${rec.current_demand_kg} kg` : `${rec.predicted_demand_kg} kg`}</div>
                      <div>🤖 <strong>Predicted Demand:</strong> {rec.predicted_demand_kg} kg</div>
                      <div>📍 <strong>Distance:</strong> {rec.distance_km} km</div>
                      <div>📦 <strong>NGO Capacity:</strong> {rec.ngo_capacity_kg ? `${rec.ngo_capacity_kg} kg` : '200 kg'}</div>
                      <div>⏱️ <strong>Food Expiry Time:</strong> {rec.expiry_hours || selectedListing.expiry_hours} hours remaining</div>
                      <div>🍲 <strong>Type Match:</strong> {rec.food_type_match ? 'Exact Match' : 'Compatible'}</div>
                    </div>

                    {/* Clear Recommendation Reasons Tags */}
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {rec.reasons.map((r, rIdx) => (
                        <span key={rIdx} style={{ background: '#e2e8f0', color: '#1e293b', fontSize: '0.75rem', padding: '3px 8px', borderRadius: '6px', fontWeight: 600 }}>
                          {r}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
