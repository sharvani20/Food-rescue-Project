import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UtensilsCrossed, AlertCircle } from 'lucide-react';

export const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'RESTAURANT',
    phone: '',
    address: 'Dwaraka Nagar 2nd Lane, Visakhapatnam, AP 530016',
    latitude: 17.7270,
    longitude: 83.3085,
    ngo_category: 'Homeless Shelter',
    daily_capacity_kg: 100
  });

  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await register(formData);
      navigate(formData.role === 'NGO' ? '/ngo' : '/donor');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '540px', margin: '40px auto' }}>
      <div className="card">
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ display: 'inline-flex', background: '#ecfdf5', color: '#059669', padding: '12px', borderRadius: '50%', marginBottom: '12px' }}>
            <UtensilsCrossed size={32} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800 }}>Create an Account</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Join the AI Surplus Food Rescue Network</p>
        </div>

        {error && (
          <div style={{ background: '#fef2f2', color: '#dc2626', padding: '10px 14px', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Account Role</label>
            <select name="role" className="form-control" value={formData.role} onChange={handleChange}>
              <option value="RESTAURANT">Restaurant / Food Donor</option>
              <option value="NGO">NGO / Shelter / Food Bank</option>
            </select>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Organization Name</label>
              <input type="text" name="name" className="form-control" value={formData.name} onChange={handleChange} required placeholder="e.g. Golden Gate Bistro" />
            </div>
            <div className="form-group">
              <label className="form-label">Email Address</label>
              <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required placeholder="contact@donor.com" />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Password</label>
              <input type="password" name="password" className="form-control" value={formData.password} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input type="text" name="phone" className="form-control" value={formData.phone} onChange={handleChange} placeholder="+1 (415) 555-0100" />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Address</label>
            <input type="text" name="address" className="form-control" value={formData.address} onChange={handleChange} required />
          </div>

          {formData.role === 'NGO' && (
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">NGO Category</label>
                <select name="ngo_category" className="form-control" value={formData.ngo_category} onChange={handleChange}>
                  <option value="Homeless Shelter">Homeless Shelter</option>
                  <option value="Food Bank">Food Bank</option>
                  <option value="Community Kitchen">Community Kitchen</option>
                  <option value="Orphanage & Youth Shelter">Orphanage & Youth Shelter</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Daily Capacity (kg)</label>
                <input type="number" name="daily_capacity_kg" className="form-control" value={formData.daily_capacity_kg} onChange={handleChange} required />
              </div>
            </div>
          )}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '12px' }} disabled={submitting}>
            {submitting ? 'Registering...' : 'Register Account'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: '0.85rem', marginTop: '20px', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Sign In</Link>
        </p>
      </div>
    </div>
  );
};
