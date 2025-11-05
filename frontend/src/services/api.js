import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Restaurant APIs
export const restaurantAPI = {
  getAll: (params) => api.get('/restaurants', { params }),
  getById: (id) => api.get(`/restaurants/${id}`),
  getCities: () => api.get('/restaurants/cities'),
  getCategories: () => api.get('/restaurants/categories')
};

// Review APIs
export const reviewAPI = {
  getByRestaurant: (restaurantId) => api.get(`/reviews/restaurant/${restaurantId}`),
  create: (data) => api.post('/reviews', data)
};

// Rating APIs
export const ratingAPI = {
  create: (data) => api.post('/ratings', data),
  getUserRatings: () => api.get('/ratings/user')
};

// Analytics APIs
export const analyticsAPI = {
  getTopRated: () => api.get('/analytics/top-rated'),
  getCityStats: () => api.get('/analytics/city-stats')
};

export default api;