import React, { useState, useEffect } from 'react';
import { adminAPI } from '../services/api';
import { ShieldAlert, Utensils, HeartHandshake, Leaf, Brain, RefreshCw, Users, Truck } from 'lucide-react';

export const AdminDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [retraining, setRetraining] = useState(false);

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      const [analyticsRes, usersRes] = await Promise.all([
        adminAPI.getAnalytics(),
        adminAPI.getUsers()
      ]);
      setAnalytics(analyticsRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      console.error("Error loading admin analytics", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrainML = async () => {
    setRetraining(true);
    try {
      const res = await adminAPI.retrainMl();
      alert(`✅ ML Model retrained successfully! R² Score: ${res.data.r2_score}, MAE: ${res.data.mae} kg`);
      fetchAdminData();
    } catch (err) {
      alert("Failed to retrain ML model.");
    } finally {
      setRetraining(false);
    }
  };

  if (loading || !analytics) {
    return <div style={{ color: 'var(--text-muted)', padding: '40px 0' }}>Loading system analytics...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={28} color="#6b21a8" />
            Admin Analytics & Platform Dashboard
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Impact metrics, food rescue totals, CO₂ emissions saved, and ML model performance.
          </p>
        </div>
        <div style={{ background: '#f3e8ff', color: '#6b21a8', padding: '8px 16px', borderRadius: '20px', fontWeight: 700, fontSize: '0.85rem' }}>
          System Administrator
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid-4">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#ecfdf5', color: '#059669' }}>
            <Utensils size={26} />
          </div>
          <div>
            <div className="metric-val">{analytics.total_food_rescued_kg} kg</div>
            <div className="metric-lbl">Total Food Rescued ({analytics.total_meals_rescued} meals)</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#f0fdf4', color: '#16a34a' }}>
            <Leaf size={26} />
          </div>
          <div>
            <div className="metric-val">{analytics.co2_emissions_saved_kg} kg</div>
            <div className="metric-lbl">CO₂ Emissions Avoided</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#dbeafe', color: '#1d4ed8' }}>
            <Truck size={26} />
          </div>
          <div>
            <div className="metric-val">{analytics.completed_deliveries_count}</div>
            <div className="metric-lbl">Completed Rescue Deliveries</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: '#f3e8ff', color: '#6b21a8' }}>
            <Users size={26} />
          </div>
          <div>
            <div className="metric-val">{analytics.total_donors + analytics.total_ngos}</div>
            <div className="metric-lbl">Active Network Partners</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* ML Demand Prediction Model Performance Card */}
        <div className="card">
          <div className="card-title" style={{ justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Brain size={22} color="#4f46e5" />
              <span>scikit-learn ML Demand Model</span>
            </div>
            <button className="btn btn-accent btn-sm" onClick={handleRetrainML} disabled={retraining}>
              <RefreshCw size={14} className={retraining ? 'spin' : ''} />
              {retraining ? 'Retraining...' : 'Retrain ML Model'}
            </button>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
            RandomForestRegressor trained on historical NGO demand, day of week, hour, location cluster, and capacity.
          </p>

          <div className="grid-2" style={{ gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: '#f8fafc', border: '1px solid var(--border)', padding: '12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>R² Score (Accuracy)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#059669' }}>
                {(analytics.ml_model_metrics?.r2_score * 100).toFixed(1)}%
              </div>
            </div>

            <div style={{ background: '#f8fafc', border: '1px solid var(--border)', padding: '12px', borderRadius: '10px' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 700 }}>Mean Absolute Error (MAE)</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#4f46e5' }}>
                {analytics.ml_model_metrics?.mae} kg
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
            <span>Dataset size: <strong>{analytics.ml_model_metrics?.dataset_size} samples</strong></span>
            <span>Model: <strong>RandomForest (100 estimators)</strong></span>
          </div>
        </div>

        {/* Category Breakdown Card */}
        <div className="card">
          <div className="card-title">
            <Utensils size={22} color="#059669" />
            <span>Food Category Distribution</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '8px' }}>
            {Object.entries(analytics.category_breakdown || {}).map(([cat, count]) => {
              const pct = (count / Math.max(1, analytics.active_listings_count + analytics.completed_deliveries_count)) * 100;
              return (
                <div key={cat}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600, marginBottom: '4px' }}>
                    <span>{cat}</span>
                    <span>{count} listings</span>
                  </div>
                  <div style={{ background: '#e2e8f0', height: '10px', borderRadius: '5px', overflow: 'hidden' }}>
                    <div style={{ background: 'var(--primary)', width: `${Math.min(100, Math.max(15, pct))}%`, height: '100%' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* System Users Table */}
      <div className="card">
        <div className="card-title">
          <Users size={20} color="#6b21a8" />
          <span>System Users Directory ({users.length})</span>
        </div>

        <div className="table-container">
          <table className="custom-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Name / Email</th>
                <th>Role</th>
                <th>Category / Capacity</th>
                <th>Address</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td><strong>#{u.id}</strong></td>
                  <td>
                    <strong>{u.name}</strong>
                    <br />
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{u.email}</span>
                  </td>
                  <td>
                    <span className={`role-pill role-${u.role}`}>{u.role}</span>
                  </td>
                  <td>
                    {u.role === 'NGO' ? (
                      <span>{u.ngo_category} (<strong>{u.daily_capacity_kg} kg</strong>)</span>
                    ) : (
                      <span style={{ color: 'var(--text-muted)' }}>Commercial Donor</span>
                    )}
                  </td>
                  <td><span style={{ fontSize: '0.85rem' }}>{u.address}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
