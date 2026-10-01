import axios from 'axios';

const getBaseUrl = (): string => {
  const envUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || '').trim();
  if (envUrl) {
    const clean = envUrl.endsWith('/') ? envUrl.slice(0, -1) : envUrl;
    return clean.endsWith('/api') ? clean : `${clean}/api`;
  }
  return '/api';
};

export const apiClient = axios.create({
  baseURL: getBaseUrl(),
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
