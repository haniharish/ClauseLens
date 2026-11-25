import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import toast from 'react-hot-toast';
import {
  DEFAULT_USER_PROFILE,
  INITIAL_DOCUMENTS,
  INITIAL_MONITORED_POLICIES,
  INITIAL_NOTIFICATIONS,
  INITIAL_POLICY_UPDATES,
} from '../data/mockData';
import { authService } from '../services/authService';
import { documentService } from '../services/documentService';

const AppContext = createContext(null);

const STORAGE_KEYS = {
  theme: 'clauselens_theme',
  profile: 'clauselens_user_profile',
  documents: 'clauselens_documents',
  policies: 'clauselens_monitored_policies',
  notifications: 'clauselens_notifications',
  settings: 'clauselens_settings',
  authFlag: 'clauselens_logged_in',
};

const DEFAULT_SETTINGS = {
  emailAlerts: true,
  highRiskPush: true,
  weeklyDigest: false,
  autoMonitorUpdates: true,
  twoFactorEnabled: false,
  dataRetentionDays: '90',
  compactMode: false,
};

function loadJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function AppProvider({ children }) {
  const [theme, setTheme] = useState(() => localStorage.getItem(STORAGE_KEYS.theme) || 'dark');
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const flag = localStorage.getItem(STORAGE_KEYS.authFlag);
    return flag === null ? true : flag === 'true';
  });

  const [profile, setProfile] = useState(() => loadJson(STORAGE_KEYS.profile, DEFAULT_USER_PROFILE));
  const [documents, setDocuments] = useState(() => loadJson(STORAGE_KEYS.documents, INITIAL_DOCUMENTS));
  const [monitoredPolicies, setMonitoredPolicies] = useState(() =>
    loadJson(STORAGE_KEYS.policies, INITIAL_MONITORED_POLICIES)
  );
  const [notifications, setNotifications] = useState(() =>
    loadJson(STORAGE_KEYS.notifications, INITIAL_NOTIFICATIONS)
  );
  const [policyUpdates] = useState(INITIAL_POLICY_UPDATES);
  const [settings, setSettings] = useState(() => loadJson(STORAGE_KEYS.settings, DEFAULT_SETTINGS));
  const [globalSearch, setGlobalSearch] = useState('');

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.remove('dark');
      root.classList.add('light');
    } else {
      root.classList.remove('light');
      root.classList.add('dark');
    }
    localStorage.setItem(STORAGE_KEYS.theme, theme);
  }, [theme]);

  useEffect(() => {
    if (profile.keepLocalOnly) {
      localStorage.setItem(STORAGE_KEYS.profile, JSON.stringify(profile));
    }
  }, [profile]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.documents, JSON.stringify(documents));
  }, [documents]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.policies, JSON.stringify(monitoredPolicies));
  }, [monitoredPolicies]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.notifications, JSON.stringify(notifications));
  }, [notifications]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify(settings));
  }, [settings]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const login = async (credentials) => {
    const res = await authService.login(credentials);
    setProfile((prev) => ({
      ...prev,
      email: res.user.email,
      fullName: res.user.fullName || prev.fullName,
    }));
    setIsAuthenticated(true);
    localStorage.setItem(STORAGE_KEYS.authFlag, 'true');
    toast.success('Signed in to ClauseLens');
    return res;
  };

  const register = async (payload) => {
    const res = await authService.register(payload);
    setProfile((prev) => ({
      ...prev,
      fullName: res.user.fullName,
      email: res.user.email,
      avatarInitials: res.user.avatarInitials,
    }));
    setIsAuthenticated(true);
    localStorage.setItem(STORAGE_KEYS.authFlag, 'true');
    toast.success('Account created successfully');
    return res;
  };

  const logout = async () => {
    await authService.logout();
    setIsAuthenticated(false);
    localStorage.setItem(STORAGE_KEYS.authFlag, 'false');
    toast('Signed out of ClauseLens', { icon: '👋' });
  };

  const addAnalyzedDocument = (newDoc) => {
    setDocuments((prev) => [newDoc, ...prev]);
    setNotifications((prev) => [
      {
        id: `notif-${Date.now()}`,
        title: `Analysis Completed: ${newDoc.name}`,
        description: `${newDoc.clausesFound} clauses extracted. Overall risk score: ${newDoc.riskScore}/100 (Demo).`,
        timestamp: 'Just now',
        severity: newDoc.riskScore >= 70 ? 'critical' : 'info',
        category: 'Analysis Completed',
        read: false,
        link: `/analysis/${newDoc.id}`,
      },
      ...prev,
    ]);
  };

  const deleteDocument = (id) => {
    setDocuments((prev) => prev.filter((d) => d.id !== id));
    toast.success('Document removed');
  };

  const reanalyzeDocument = (id) => {
    setDocuments((prev) =>
      prev.map((d) =>
        d.id === id
          ? {
              ...d,
              dateAnalyzed: new Date().toISOString().split('T')[0],
            }
          : d
      )
    );
    toast.success('Re-analysis completed using updated profile');
  };

  const toggleSaveClause = (docId, clauseId) => {
    setDocuments((prev) =>
      prev.map((doc) =>
        doc.id !== docId
          ? doc
          : {
              ...doc,
              clauses: doc.clauses.map((c) =>
                c.id === clauseId ? { ...c, saved: !c.saved } : c
              ),
            }
      )
    );
  };

  const addMonitoredPolicy = async (payload) => {
    const newPolicy = await documentService.addMonitoredPolicy(payload);
    setMonitoredPolicies((prev) => [newPolicy, ...prev]);
    toast.success(`Started monitoring ${payload.service}`);
    return newPolicy;
  };

  const togglePolicyMonitoring = (id) => {
    setMonitoredPolicies((prev) =>
      prev.map((p) =>
        p.id === id
          ? { ...p, status: p.status === 'Active' ? 'Paused' : 'Active' }
          : p
      )
    );
  };

  const removeMonitoredPolicy = (id) => {
    setMonitoredPolicies((prev) => prev.filter((p) => p.id !== id));
    toast.success('Policy removed from monitoring');
  };

  const markNotificationRead = (id) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllNotificationsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    toast.success('All notifications marked as read');
  };

  const deleteNotification = (id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    toast.success('Notifications cleared');
  };

  const updateProfile = (nextProfile) => {
    const initials = (nextProfile.fullName || 'AS')
      .split(' ')
      .filter(Boolean)
      .map((s) => s[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
    setProfile({ ...nextProfile, avatarInitials: initials || 'CL' });
    toast.success('Personalization profile saved');
  };

  const updateSettings = (patch) => {
    setSettings((prev) => ({ ...prev, ...patch }));
  };

  const resetDemoData = () => {
    setDocuments(INITIAL_DOCUMENTS);
    setMonitoredPolicies(INITIAL_MONITORED_POLICIES);
    setNotifications(INITIAL_NOTIFICATIONS);
    setProfile(DEFAULT_USER_PROFILE);
    setSettings(DEFAULT_SETTINGS);
    toast.success('Demo workspace restored to defaults');
  };

  const unreadCount = useMemo(
    () => notifications.filter((n) => !n.read).length,
    [notifications]
  );

  const value = {
    theme,
    toggleTheme,
    isAuthenticated,
    login,
    register,
    logout,
    profile,
    updateProfile,
    documents,
    addAnalyzedDocument,
    deleteDocument,
    reanalyzeDocument,
    toggleSaveClause,
    monitoredPolicies,
    addMonitoredPolicy,
    togglePolicyMonitoring,
    removeMonitoredPolicy,
    policyUpdates,
    notifications,
    unreadCount,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    clearAllNotifications,
    settings,
    updateSettings,
    globalSearch,
    setGlobalSearch,
    resetDemoData,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}
