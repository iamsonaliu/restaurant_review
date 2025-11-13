// api.js — fetch-based API client with compatibility wrappers for previous axios-style exports

const API_BASE_URL = 'http://localhost:5000/api';

// Custom error that preserves HTTP status
export class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Helper that safely parses JSON (or returns text if not JSON)
async function parseResponseBody(response) {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch (e) {
    return text;
  }
}

// Core fetch wrapper
async function apiCall(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const token = localStorage.getItem('token');

  // Default method is GET
  const method = options.method ? options.method.toUpperCase() : 'GET';

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  const config = {
    method,
    headers,
  };

  // Only attach body for non-GET/HEAD requests
  if (options.body !== undefined && method !== 'GET' && method !== 'HEAD') {
    // If caller passed a plain object, we stringify; if already string, send as-is
    config.body = typeof options.body === 'string' ? options.body : JSON.stringify(options.body);
  }

  try {
    const response = await fetch(url, config);
    const data = await parseResponseBody(response);

    if (!response.ok) {
      // data may be string or object; try to extract message
      const message = data && typeof data === 'object' ? (data.error || data.message || JSON.stringify(data)) : (data || 'API request failed');
      throw new APIError(message, response.status);
    }

    return data;
  } catch (error) {
    // Network errors or our thrown APIError
    if (error instanceof APIError) throw error;
    console.error(`API Error (${endpoint}):`, error);
    throw new APIError(error.message || 'Network error', error.status || 0);
  }
}

// --- Authentication API ---
export const authAPI = {
  register: async (username, email, password) => {
    return apiCall('/auth/register', {
      method: 'POST',
      body: { username, email, password },
    });
  },

  login: async (email, password) => {
    const data = await apiCall('/auth/login', {
      method: 'POST',
      body: { email, password },
    });

    if (data && data.token) {
      localStorage.setItem('token', data.token);
      if (data.user) localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },
};

// --- Restaurants API ---
export const restaurantsAPI = {
  getAll: async (filters = {}) => {
    const params = new URLSearchParams();

    if (filters.city) params.append('city', filters.city);
    if (filters.cuisine) params.append('cuisine', filters.cuisine);
    if (filters.search) params.append('search', filters.search);
    if (filters.min_rating) params.append('min_rating', filters.min_rating);
    if (filters.limit) params.append('limit', filters.limit);
    if (filters.offset) params.append('offset', filters.offset);

    const queryString = params.toString();
    const endpoint = `/restaurants${queryString ? '?' + queryString : ''}`; // FIXED: no extra slash before ?

    return apiCall(endpoint);
  },

  getById: async (restaurantId) => {
    return apiCall(`/restaurants/${restaurantId}`);
  },

  getCities: async () => {
    return apiCall('/restaurants/cities');
  },

  getCategories: async () => {
    return apiCall('/restaurants/categories');
  },

  search: async (query, filters = {}) => {
    const params = new URLSearchParams({ q: query });

    if (filters.city) params.append('city', filters.city);
    if (filters.cuisine) params.append('cuisine', filters.cuisine);
    if (filters.min_rating) params.append('min_rating', filters.min_rating);
    if (filters.max_price) params.append('max_price', filters.max_price);

    return apiCall(`/restaurants/search?${params.toString()}`);
  },
};

// --- Reviews API ---
export const reviewsAPI = {
  getByRestaurant: async (restaurantId) => {
    return apiCall(`/reviews/restaurant/${restaurantId}`);
  },

  create: async (restaurantId, reviewText) => {
    return apiCall('/reviews', {
      method: 'POST',
      body: { restaurant_id: restaurantId, review_text: reviewText },
    });
  },
};

// --- Ratings API ---
export const ratingsAPI = {
  create: async (restaurantId, ratingValue) => {
    return apiCall('/ratings', {
      method: 'POST',
      body: { restaurant_id: restaurantId, rating_value: ratingValue },
    });
  },

  getUserRatings: async () => {
    return apiCall('/ratings/user');
  },
};

// --- Analytics API ---
export const analyticsAPI = {
  getTopRated: async () => {
    return apiCall('/analytics/top-rated');
  },

  getCityStats: async () => {
    return apiCall('/analytics/city-stats');
  },
};

// --- Health check ---
export const healthCheck = async () => {
  return apiCall('/health');
};

// --- Compatibility wrappers for previous axios-based exports ---
// These let you keep older imports like `import { restaurantAPI } from './api'` working
export const restaurantAPI = {
  getAll: (params) => restaurantsAPI.getAll(params),
  getById: (id) => restaurantsAPI.getById(id),
  getCities: () => restaurantsAPI.getCities(),
  getCategories: () => restaurantsAPI.getCategories(),
};

export const reviewAPI = {
  // old code expected create(data)
  getByRestaurant: (restaurantId) => reviewsAPI.getByRestaurant(restaurantId),
  create: (data) => {
    // Accept either (restaurantId, reviewText) or a data object
    if (data && data.restaurant_id && data.review_text) {
      return reviewsAPI.create(data.restaurant_id, data.review_text);
    }
    // Otherwise expect { restaurantId, reviewText }
    if (data && (data.restaurantId || data.restaurant_id) && (data.reviewText || data.review_text)) {
      return reviewsAPI.create(data.restaurantId || data.restaurant_id, data.reviewText || data.review_text);
    }
    // Fallback: if called with (restaurantId, text)
    if (arguments.length === 2) {
      return reviewsAPI.create(arguments[0], arguments[1]);
    }
    throw new Error('Invalid arguments to reviewAPI.create');
  },
};

export const ratingAPI = {
  create: (data) => {
    // Accept either (dataObj) or (restaurantId, ratingValue)
    if (data && typeof data === 'object' && (data.restaurant_id || data.restaurantId)) {
      return ratingsAPI.create(data.restaurant_id || data.restaurantId, data.rating_value || data.value || data.ratingValue);
    }
    if (arguments.length === 2) {
      return ratingsAPI.create(arguments[0], arguments[1]);
    }
    throw new Error('Invalid arguments to ratingAPI.create');
  },
  getUserRatings: () => ratingsAPI.getUserRatings(),
};

// small apiInstance that mimics a tiny portion of axios instance used in the app
export const apiInstance = {
  get: (path, config) => apiCall(path, { method: 'GET', ...(config || {}) }),
  post: (path, body, config) => apiCall(path, { method: 'POST', body, ...(config || {}) }),
};

// Default grouped export (convenience)
export default {
  auth: authAPI,
  restaurants: restaurantsAPI,
  reviews: reviewsAPI,
  ratings: ratingsAPI,
  analytics: analyticsAPI,
  healthCheck,
  APIError,
};
