import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configura axios defaults
axios.defaults.baseURL = API_URL;

// Interceptor per aggiungere token automaticamente
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor per gestire errori di autenticazione
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Services
export const authAPI = {
  login: (credentials) => axios.post('/auth/login', credentials),
  register: (userData) => axios.post('/auth/register', userData),
  getProfile: () => axios.get('/auth/me')
};

export const bookingsAPI = {
  getAll: () => axios.get('/bookings/'),
  create: (data) => axios.post('/bookings/', data),
  update: (id, data) => axios.put(`/bookings/${id}`, data),
  delete: (id) => axios.delete(`/bookings/${id}`),
  getHistory: () => axios.get('/bookings/history')
};

export const spacesAPI = {
  getAll: (params = {}) => axios.get('/spaces/', { params }),
  getById: (id) => axios.get(`/spaces/${id}`),
  getAvailability: (id, date) => axios.get(`/spaces/${id}/availability`, { params: { date } }),
  getTypes: () => axios.get('/spaces/types/list'),
  getMaterials: (id) => axios.get(`/spaces/${id}/materials`)
};

export const chatAPI = {
  sendMessage: (message) => axios.post('/chat/', { message }),
  getSpaces: () => axios.get('/chat/spaces')
};

export default axios;