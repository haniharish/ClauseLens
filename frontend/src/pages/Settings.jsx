import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Lock,
  LogOut,
  Moon,
  Palette,
  RefreshCcw,
  Shield,
  Sliders,
  Sun,
  User,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';

const TABS = [
  { id: 'account', label: 'Account Settings', icon: User },
  { id: 'profile', label: 'Profile Preferences', icon: Sliders },
  { id: 'notifications', label: 'Notification Preferences', icon: Bell },
  { id: 'privacy', label: 'Privacy Settings', icon: Shield },
  { id: 'theme', label: 'Theme Settings', icon: Palette },
  { id: 'security', label: 'Security Settings', icon: Lock },
];

export default function Settings() {
  const {
    theme,
    toggleTheme,
    profile,
    settings,
    updateSettings,
    logout,
    resetDemoData,
  } = useApp();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('account');

  const handleToggle = (key, label) => {
    updateSettings({ [key]: !settings[key] });
    toast.success(`${label} updated`);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">Settings</h1>
        <p className="mt-1 text-sm text-[var(--cl-muted)]">
          Manage your ClauseLens account, notification alerts, privacy controls, and appearance.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Settings Navigation Tabs */}
        <div className="glass-card p-3 lg:col-span-4 h-fit space-y-1">
          {TABS.map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-left text-xs font-semibold transition ${
                  active
                    ? 'bg-[#9B7AFF]/20 text-[var(--cl-text)] border border-[#9B7AFF]/40'
                    : 'text-[var(--cl-muted)] hover:bg-white/5 hover:text-[var(--cl-text)] border border-transparent'
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? 'text-[#9B7AFF]' : ''}`} />
                {tab.label}
              </button>
            );
          })}

          <div className="pt-2 mt-2 border-t border-[var(--cl-border)]">
            <button
              onClick={async () => {
                await logout();
                navigate('/login');
              }}
              className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-left text-xs font-semibold text-red-400 transition hover:bg-red-500/10"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>

        {/* Settings Panel Content */}
        <div className="glass-card p-6 lg:col-span-8 space-y-6">
          {activeTab === 'account' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">Account Settings</h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1.5 block text-xs text-[var(--cl-muted)]">Account Name</label>
                  <input type="text" readOnly value={profile.fullName} className="cl-input opacity-80" />
                </div>
                <div>
                  <label className="mb-1.5 block text-xs text-[var(--cl-muted)]">Primary Email</label>
                  <input type="email" readOnly value={profile.email} className="cl-input opacity-80" />
                </div>
              </div>
              <div className="flex flex-wrap gap-3 pt-2">
                <button onClick={() => navigate('/profile')} className="cl-btn-primary text-xs">
                  Edit Personal Profile
                </button>
                <button onClick={resetDemoData} className="cl-btn-secondary text-xs">
                  <RefreshCcw className="h-3.5 w-3.5" />
                  Restore Demo Data
                </button>
              </div>
            </div>
          )}

          {activeTab === 'profile' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">Profile Preferences</h2>
              <p className="text-xs text-[var(--cl-muted)]">
                Current personalization dimensions: <strong>{profile.ageGroup}</strong> ·{' '}
                <strong>{profile.intendedUse?.join(', ')}</strong> ·{' '}
                <strong>{profile.jurisdiction}</strong>
              </p>
              <label className="flex items-center justify-between rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/50 p-4 cursor-pointer">
                <div>
                  <p className="text-sm font-medium text-[var(--cl-text)]">
                    Auto-Monitor Uploaded Policies
                  </p>
                  <p className="text-xs text-[var(--cl-muted)]">
                    Automatically track URL-based documents for future version changes
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.autoMonitorUpdates}
                  onChange={() => handleToggle('autoMonitorUpdates', 'Auto-monitoring')}
                  className="h-4 w-4 accent-[#9B7AFF]"
                />
              </label>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">
                Notification Preferences
              </h2>
              {[
                {
                  key: 'highRiskPush',
                  title: 'High-Risk Clause Alerts',
                  desc: 'Instant alerts when a newly analyzed or updated policy introduces high-risk clauses.',
                },
                {
                  key: 'emailAlerts',
                  title: 'Version-Diff Email Notifications',
                  desc: 'Receive summaries when monitored policies change significantly.',
                },
                {
                  key: 'weeklyDigest',
                  title: 'Weekly Risk Digest',
                  desc: 'Weekly summary of policy monitoring activity.',
                },
              ].map((item) => (
                <label
                  key={item.key}
                  className="flex items-center justify-between rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/50 p-4 cursor-pointer"
                >
                  <div>
                    <p className="text-sm font-medium text-[var(--cl-text)]">{item.title}</p>
                    <p className="text-xs text-[var(--cl-muted)]">{item.desc}</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={settings[item.key]}
                    onChange={() => handleToggle(item.key, item.title)}
                    className="h-4 w-4 accent-[#9B7AFF]"
                  />
                </label>
              ))}
            </div>
          )}

          {activeTab === 'privacy' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">Privacy Settings</h2>
              <div>
                <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-muted)]">
                  Analyzed Document Retention (Local / Backend Policy)
                </label>
                <select
                  value={settings.dataRetentionDays}
                  onChange={(e) => {
                    updateSettings({ dataRetentionDays: e.target.value });
                    toast.success('Retention preference saved');
                  }}
                  className="cl-input max-w-xs cursor-pointer"
                >
                  <option value="30">30 days</option>
                  <option value="90">90 days</option>
                  <option value="180">180 days</option>
                  <option value="manual">Delete manually only</option>
                </select>
              </div>
              <p className="text-xs text-[var(--cl-muted)]">
                Device-local profile storage is currently{' '}
                <strong className="text-[var(--cl-text)]">
                  {profile.keepLocalOnly ? 'Enabled' : 'Disabled'}
                </strong>
                .
              </p>
            </div>
          )}

          {activeTab === 'theme' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">Theme Settings</h2>
              <p className="text-xs text-[var(--cl-muted)]">
                Switch between ClauseLens Signature Dark Mode and Light Mode.
              </p>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <button
                  onClick={() => theme !== 'dark' && toggleTheme()}
                  className={`flex items-center gap-3 rounded-xl border p-4 text-left transition ${
                    theme === 'dark'
                      ? 'border-[#9B7AFF] bg-[#9B7AFF]/15'
                      : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/40'
                  }`}
                >
                  <Moon className="h-5 w-5 text-[#9B7AFF]" />
                  <div>
                    <p className="text-sm font-semibold text-[var(--cl-text)]">
                      Dark SaaS Theme (Default)
                    </p>
                    <p className="text-xs text-[var(--cl-muted)]">#080A12 navy + #9B7AFF accent</p>
                  </div>
                </button>
                <button
                  onClick={() => theme !== 'light' && toggleTheme()}
                  className={`flex items-center gap-3 rounded-xl border p-4 text-left transition ${
                    theme === 'light'
                      ? 'border-[#9B7AFF] bg-[#9B7AFF]/15'
                      : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/40'
                  }`}
                >
                  <Sun className="h-5 w-5 text-amber-400" />
                  <div>
                    <p className="text-sm font-semibold text-[var(--cl-text)]">Light Theme</p>
                    <p className="text-xs text-[var(--cl-muted)]">High-contrast daylight surface</p>
                  </div>
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">Security Settings</h2>
              <label className="flex items-center justify-between rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/50 p-4 cursor-pointer">
                <div>
                  <p className="text-sm font-medium text-[var(--cl-text)]">
                    Two-Factor Authentication (2FA)
                  </p>
                  <p className="text-xs text-[var(--cl-muted)]">
                    Prepared for Django JWT + TOTP verification
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={settings.twoFactorEnabled}
                  onChange={() => handleToggle('twoFactorEnabled', '2FA preference')}
                  className="h-4 w-4 accent-[#9B7AFF]"
                />
              </label>
              <button
                onClick={() => toast.success('Password update flow is ready for backend integration')}
                className="cl-btn-secondary text-xs"
              >
                Change Password
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
