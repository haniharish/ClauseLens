import api, { USE_MOCK_API } from './api';
import {
  RISK_DISTRIBUTION_DATA,
  RISK_TREND_DATA,
  VERSION_COMPARISONS,
  DEFAULT_USER_PROFILE,
} from '../data/mockData';

export const analysisService = {
  async getRiskAnalytics() {
    if (USE_MOCK_API) {
      return {
        overallScore: 72,
        status: 'Moderate',
        distribution: RISK_DISTRIBUTION_DATA,
        trend: RISK_TREND_DATA,
      };
    }
    const { data } = await api.get('/analysis/risk-overview/');
    return data;
  },

  async getVersionComparisons() {
    if (USE_MOCK_API) {
      return VERSION_COMPARISONS;
    }
    const { data } = await api.get('/versions/');
    return data;
  },

  async getProfile() {
    if (USE_MOCK_API) {
      const saved = localStorage.getItem('clauselens_user_profile');
      return saved ? JSON.parse(saved) : DEFAULT_USER_PROFILE;
    }
    const { data } = await api.get('/profile/');
    return data;
  },

  async updateProfile(profileData) {
    if (USE_MOCK_API) {
      localStorage.setItem('clauselens_user_profile', JSON.stringify(profileData));
      return profileData;
    }
    const { data } = await api.put('/profile/', profileData);
    return data;
  },
};
