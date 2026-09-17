import axios from 'axios';

const API_BASE = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Attach JWT Token if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('skillalpha_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response Interceptor: Unwrap standardized API response
apiClient.interceptors.response.use(
  (response) => {
    const data = response.data;
    if (data && data.error) {
      return Promise.reject(new Error(data.error.message || 'API Error'));
    }
    return data && data.data !== undefined ? data.data : data;
  },
  (error) => {
    const msg = error.response?.data?.error?.message || error.message || 'Network error';
    return Promise.reject(new Error(msg));
  }
);
