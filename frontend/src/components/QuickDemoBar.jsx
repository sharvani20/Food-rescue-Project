import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Zap, Utensils, HeartHandshake, ShieldCheck } from 'lucide-react';

export const QuickDemoBar = () => {
  const { user, quickDemoLogin } = useAuth();

  return (
    <div className="demo-bar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 600 }}>
        <Zap size={16} color="#fbbf24" />
        <span>Quick Demo Login for Reviewers:</span>
      </div>
      <div className="demo-btn-group">
        <button
          className="demo-btn"
          style={{ borderColor: user?.role === 'RESTAURANT' ? '#10b981' : undefined }}
          onClick={() => quickDemoLogin('RESTAURANT')}
        >
          <Utensils size={13} style={{ marginRight: '4px' }} />
          Donor: Spicy Venue Restaurant
        </button>
        <button
          className="demo-btn"
          style={{ borderColor: user?.role === 'NGO' ? '#10b981' : undefined }}
          onClick={() => quickDemoLogin('NGO')}
        >
          <HeartHandshake size={13} style={{ marginRight: '4px' }} />
          NGO: Akshaya Patra Vizag
        </button>
        <button
          className="demo-btn"
          style={{ borderColor: user?.role === 'ADMIN' ? '#10b981' : undefined }}
          onClick={() => quickDemoLogin('ADMIN')}
        >
          <ShieldCheck size={13} style={{ marginRight: '4px' }} />
          Admin: System Administrator
        </button>
      </div>
    </div>
  );
};
