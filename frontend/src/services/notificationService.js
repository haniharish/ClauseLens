import api, { USE_MOCK_API } from './api';
import { INITIAL_NOTIFICATIONS } from '../data/mockData';

export const notificationService = {
  async getNotifications() {
    if (USE_MOCK_API) return INITIAL_NOTIFICATIONS;
    const { data } = await api.get('/notifications/');
    return data;
  },

  async markAsRead(id) {
    if (USE_MOCK_API) return { id, read: true };
    const { data } = await api.patch(`/notifications/${id}/`, { read: true });
    return data;
  },

  async markAllAsRead() {
    if (USE_MOCK_API) return { success: true };
    const { data } = await api.post('/notifications/mark-all-read/');
    return data;
  },
};
