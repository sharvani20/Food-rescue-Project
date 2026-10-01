import React, { useState, useEffect } from 'react';
import { routingAPI } from '../services/api';
import { LeafletMap } from '../components/LeafletMap';
import { Route, Truck, MapPin, Play, RefreshCw, Clock, ArrowRight } from 'lucide-react';

export const RoutePlannerPage = () => {
  const [routeData, setRouteData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [vehicleCapacity, setVehicleCapacity] = useState(150);
  const [numVehicles, setNumVehicles] = useState(2);

  useEffect(() => {
    runOptimizer();
  }, []);

  const runOptimizer = async () => {
    setLoading(true);
    try {
      const res = await routingAPI.optimizeRoutes(vehicleCapacity, numVehicles);
      setRouteData(res.data);
    } catch (err) {
      console.error("Error optimizing routes", err);
      alert("Failed to compute OR-Tools route solution.");
    } finally {
      setLoading(false);
    }
  };

  // Build map markers and polylines from OR-Tools VRP output
  const markers = [];
  const polylines = [];

  const routeColors = ['#4f46e5', '#059669', '#d97706', '#dc2626'];

  if (routeData && routeData.routes) {
    routeData.routes.forEach((route, rIdx) => {
      const color = routeColors[rIdx % routeColors.length];

      // Add polyline for this vehicle route
      if (route.polyline_coords && route.polyline_coords.length > 0) {
        polylines.push({
          color: color,
          coords: route.polyline_coords
        });
      }

      // Add markers for stops
      route.stops.forEach((stop) => {
        markers.push({
          id: `route-${route.vehicle_id}-${stop.step_number}`,
          lat: stop.latitude,
          lng: stop.longitude,
          title: stop.location_name,
          type: stop.type,
          address: stop.address,
          notes: `${route.driver_name} • Stop #${stop.step_number}`
        });
      });
    });
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Route size={28} color="#4f46e5" />
            Google OR-Tools Route Optimizer
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Vehicle Routing Problem (VRP) solver with capacity constraints and pickup-delivery sequence optimization.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <label style={{ fontWeight: 600 }}>Van Cap (kg):</label>
            <input
              type="number"
              className="form-control"
              style={{ width: '80px', padding: '6px 8px' }}
              value={vehicleCapacity}
              onChange={(e) => setVehicleCapacity(parseFloat(e.target.value))}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <label style={{ fontWeight: 600 }}>Vehicles:</label>
            <input
              type="number"
              className="form-control"
              style={{ width: '70px', padding: '6px 8px' }}
              value={numVehicles}
              onChange={(e) => setNumVehicles(parseInt(e.target.value))}
            />
          </div>

          <button className="btn btn-accent" onClick={runOptimizer} disabled={loading}>
            {loading ? <RefreshCw size={16} className="spin" /> : <Play size={16} />}
            Run OR-Tools Solver
          </button>
        </div>
      </div>

      {/* KPI Stats Bar */}
      {routeData && (
        <div className="grid-3">
          <div className="metric-card">
            <div className="metric-icon" style={{ background: '#eef2ff', color: '#4f46e5' }}>
              <Truck size={28} />
            </div>
            <div>
              <div className="metric-val">{routeData.num_vehicles_used} Vehicles</div>
              <div className="metric-lbl">Active Dispatch Fleet</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: '#ecfdf5', color: '#059669' }}>
              <Route size={28} />
            </div>
            <div>
              <div className="metric-val">{routeData.total_distance_km} km</div>
              <div className="metric-lbl">Total Traveled Distance</div>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon" style={{ background: '#fffbeb', color: '#d97706' }}>
              <MapPin size={28} />
            </div>
            <div>
              <div className="metric-val">{routeData.total_food_delivered_kg} kg</div>
              <div className="metric-lbl">Total Food Scheduled for Rescue</div>
            </div>
          </div>
        </div>
      )}

      {/* Leaflet Map Display */}
      <div className="card">
        <div className="card-title">
          <MapPin size={20} color="#4f46e5" />
          <span>Interactive VRP Dispatch Route Map</span>
        </div>
        <LeafletMap markers={markers} polylines={polylines} height="480px" />
      </div>

      {/* Step-by-Step Vehicle Route Sequences */}
      {routeData && routeData.routes && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {routeData.routes.map((route, rIdx) => {
            const color = routeColors[rIdx % routeColors.length];
            return (
              <div key={route.vehicle_id} className="card" style={{ borderLeft: `6px solid ${color}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Truck size={22} color={color} />
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800 }}>{route.driver_name}</h3>
                  </div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '0.9rem' }}>
                    <div>Total Distance: <strong>{route.total_distance_km} km</strong></div>
                    <div>Vehicle Load: <strong>{route.total_load_kg} kg</strong></div>
                  </div>
                </div>

                <div className="table-container">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>Stop #</th>
                        <th>Type</th>
                        <th>Location & Address</th>
                        <th>Item & Payload</th>
                        <th>Est. Arrival</th>
                      </tr>
                    </thead>
                    <tbody>
                      {route.stops.map((stop) => (
                        <tr key={stop.step_number}>
                          <td><strong>#{stop.step_number}</strong></td>
                          <td>
                            <span className={`badge status-${stop.type === 'PICKUP' ? 'AVAILABLE' : (stop.type === 'DELIVERY' ? 'DELIVERED' : 'MATCHED')}`}>
                              {stop.type}
                            </span>
                          </td>
                          <td>
                            <strong>{stop.location_name}</strong>
                            <br />
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{stop.address}</span>
                          </td>
                          <td>
                            {stop.item_title ? (
                              <span>{stop.item_title} (<strong>{stop.quantity_kg} kg</strong>)</span>
                            ) : (
                              <span style={{ color: 'var(--text-muted)' }}>—</span>
                            )}
                          </td>
                          <td>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                              <Clock size={13} color="#4f46e5" />
                              <span>{stop.arrival_time_est}</span>
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
