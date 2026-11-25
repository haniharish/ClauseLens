import api, { USE_MOCK_API } from './api';
import { DEFAULT_USER_PROFILE } from '../data/mockData';

const AUTH_STORAGE_KEY = 'clauselens_auth_user';

export const authService = {
  async login({ email, password, rememberMe }) {
    if (USE_MOCK_API) {
      await new Promise((r) => setTimeout(r, 450));
      const user = {
        ...DEFAULT_USER_PROFILE,
        email: email || DEFAULT_USER_PROFILE.email,
      };
      localStorage.setItem('clauselens_access_token', 'mock-jwt-access-token');
      localStorage.setItem('clauselens_refresh_token', 'mock-jwt-refresh-token');
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ user, rememberMe: !!rememberMe }));
      return { user, access: 'mock-jwt-access-token' };
    }
    const { data } = await api.post('/auth/login/', { email, password });
    localStorage.setItem('clauselens_access_token', data.access);
    localStorage.setItem('clauselens_refresh_token', data.refresh);
    return data;
  },

  async register({ fullName, email, password }) {
    if (USE_MOCK_API) {
      await new Promise((r) => setTimeout(r, 500));
      const initials = (fullName || 'AS')
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
      const user = {
        ...DEFAULT_USER_PROFILE,
        fullName: fullName || DEFAULT_USER_PROFILE.fullName,
        email: email || DEFAULT_USER_PROFILE.email,
        avatarInitials: initials || 'CL',
      };
      localStorage.setItem('clauselens_access_token', 'mock-jwt-access-token');
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ user, rememberMe: true }));
      return { user, access: 'mock-jwt-access-token' };
    }
    const { data } = await api.post('/auth/register/', { full_name: fullName, email, password });
    return data;
  },

  async logout() {
    localStorage.removeItem('clauselens_access_token');
    localStorage.removeItem('clauselens_refresh_token');
    localStorage.removeItem(AUTH_STORAGE_KEY);
    if (!USE_MOCK_API) {
      try {
        await api.post('/auth/logout/');
      } catch {
        // Ignore network errors on logout
      }
    }
  },

  getStoredSession() {
    try {
      const token = localStorage.getItem('clauselens_access_token');
      const raw = localStorage.getItem(AUTH_STORAGE_KEY);
      if (!token && !raw) return null;
      return raw ? JSON.parse(raw).user : DEFAULT_USER_PROFILE;
    } catch {
      return null;
    }
  },
};
