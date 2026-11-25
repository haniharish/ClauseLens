import axios from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const USE_MOCK_API =
  import.meta.env.VITE_USE_MOCK_API !== 'false';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach JWT access token when available (Django SimpleJWT ready)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('clauselens_access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Standardized response & refresh-token readiness
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('clauselens_refresh_token');
      if (refreshToken && !USE_MOCK_API) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('clauselens_access_token', data.access);
          originalRequest.headers.Authorization = `Bearer ${data.access}`;
          return api(originalRequest);
        } catch {
          localStorage.removeItem('clauselens_access_token');
          localStorage.removeItem('clauselens_refresh_token');
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
