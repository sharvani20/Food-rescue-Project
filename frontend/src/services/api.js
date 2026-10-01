import axios from 'axios';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT token to requests if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me'),
};

export const listingsAPI = {
  getListings: (status, donor_id) => api.get('/listings', { params: { status, donor_id } }),
  createListing: (data) => api.post('/listings', data),
  deleteListing: (id) => api.delete(`/listings/${id}`),
};

export const ngoReqsAPI = {
  getRequests: (active_only = true) => api.get('/ngo-requests', { params: { active_only } }),
  createRequest: (data) => api.post('/ngo-requests', data),
};

export const matchingAPI = {
  getRecommendations: (listingId) => api.get(`/matching/recommend/${listingId}`),
  claimMatch: (listingId) => api.post(`/matching/claim/${listingId}`),
};

export const routingAPI = {
  optimizeRoutes: (capacity = 150, vehicles = 2) => 
    api.get('/routing/optimize-routes', { params: { vehicle_capacity_kg: capacity, num_vehicles: vehicles } }),
};

export const deliveriesAPI = {
  getDeliveries: (status) => api.get('/deliveries', { params: { status } }),
  updateStatus: (id, status, notes) => api.patch(`/deliveries/${id}/status`, { status, notes }),
};

export const adminAPI = {
  getAnalytics: () => api.get('/admin/analytics'),
  retrainMl: () => api.post('/admin/retrain-ml'),
  getUsers: (role) => api.get('/admin/users', { params: { role } }),
};

export default api;
