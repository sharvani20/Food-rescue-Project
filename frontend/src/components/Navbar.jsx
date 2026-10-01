import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UtensilsCrossed, LayoutDashboard, Route, ShieldAlert, LogOut, HeartHandshake } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <UtensilsCrossed size={28} />
        <span>FoodRescue AI</span>
      </Link>

      <div className="nav-links">
        {user ? (
          <>
            <Link to="/donor" className={`nav-link ${isActive('/donor') ? 'active' : ''}`}>
              <UtensilsCrossed size={16} />
              Donor Dashboard
            </Link>

            <Link to="/ngo" className={`nav-link ${isActive('/ngo') ? 'active' : ''}`}>
              <HeartHandshake size={16} />
              NGO Dashboard
            </Link>

            <Link to="/route-planner" className={`nav-link ${isActive('/route-planner') ? 'active' : ''}`}>
              <Route size={16} />
              Route Optimization
            </Link>

            <Link to="/admin" className={`nav-link ${isActive('/admin') ? 'active' : ''}`}>
              <ShieldAlert size={16} />
              Admin Analytics
            </Link>

            <div className="user-badge">
              <span className={`role-pill role-${user.role}`}>{user.role}</span>
              <span>{user.name}</span>
            </div>

            <button onClick={logout} className="btn btn-outline btn-sm" title="Logout">
              <LogOut size={16} />
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="btn btn-outline btn-sm">Sign In</Link>
            <Link to="/register" className="btn btn-primary btn-sm">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
};
