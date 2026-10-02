import axios from 'axios';
import { getSupabaseToken } from './supabase';

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

// Request Interceptor: Attach Supabase JWT Token if present
apiClient.interceptors.request.use(async (config) => {
  const token = await getSupabaseToken();
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
    if (error.response?.status === 405) {
      return Promise.reject(
        new Error(
          'API returned 405 Method Not Allowed. VITE_API_URL is missing or points to the Vercel frontend rather than the deployed backend server (e.g. Render).'
        )
      );
    }
    if (error.response?.status === 404 && typeof window !== 'undefined' && !window.location.hostname.includes('localhost')) {
      const isMissingApiEnv = !(import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL);
      if (isMissingApiEnv) {
        return Promise.reject(
          new Error(
            'API returned 404. VITE_API_URL is not configured in Vercel settings. Please set VITE_API_URL to your deployed backend URL.'
          )
        );
      }
    }
    const msg = error.response?.data?.error?.message || error.message || 'Network error';
    return Promise.reject(new Error(msg));
  }
);
