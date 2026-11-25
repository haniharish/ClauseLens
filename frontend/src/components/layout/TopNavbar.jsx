import { useLocation, useNavigate } from 'react-router-dom';
import {
  Bell,
  ChevronRight,
  Menu,
  Moon,
  Search,
  Settings,
  Sun,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

const ROUTE_TITLES = {
  '/dashboard': 'Dashboard',
  '/analyze': 'Analyze Document',
  '/documents': 'My Documents',
  '/risk-analysis': 'Risk Analysis',
  '/monitoring': 'Policy Monitoring',
  '/version-history': 'Version History',
  '/notifications': 'Notifications',
  '/profile': 'User Profile',
  '/settings': 'Settings',
};

export default function TopNavbar({ onOpenMobileMenu }) {
  const {
    theme,
    toggleTheme,
    unreadCount,
    profile,
    globalSearch,
    setGlobalSearch,
  } = useApp();
  const location = useLocation();
  const navigate = useNavigate();

  const currentTitle = location.pathname.startsWith('/analysis')
    ? 'Analysis Results'
    : ROUTE_TITLES[location.pathname] || 'Dashboard';

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter' && globalSearch.trim()) {
      navigate('/documents');
    }
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-4 border-b border-[var(--cl-border)] bg-[var(--cl-bg)]/85 px-4 backdrop-blur-md sm:px-6">
      {/* Left: Mobile Menu + Breadcrumb */}
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onOpenMobileMenu}
          className="rounded-xl border border-[var(--cl-border)] p-2 text-[var(--cl-muted)] hover:text-[var(--cl-text)] md:hidden"
          aria-label="Open navigation menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex items-center gap-1.5 text-sm min-w-0">
          <span
            onClick={() => navigate('/dashboard')}
            className="hidden sm:inline cursor-pointer text-[var(--cl-muted)] hover:text-[var(--cl-text)] transition"
          >
            ClauseLens
          </span>
          <ChevronRight className="hidden sm:inline h-4 w-4 text-[var(--cl-subtle)]" />
          <span className="truncate font-semibold text-[var(--cl-text)]">{currentTitle}</span>
        </div>
      </div>

      {/* Right: Search, Bell, Theme Toggle, Settings, Avatar */}
      <div className="flex items-center gap-2 sm:gap-3">
        <div className="relative hidden md:block w-56 lg:w-72">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--cl-muted)]" />
          <input
            type="text"
            value={globalSearch}
            onChange={(e) => setGlobalSearch(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            placeholder="Search policies, clauses..."
            className="cl-input pl-9 py-2 text-xs"
          />
        </div>

        <button
          onClick={() => navigate('/notifications')}
          className="relative flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--cl-border)] bg-[var(--cl-card)] text-[var(--cl-muted)] transition hover:border-[#9B7AFF]/40 hover:text-[var(--cl-text)]"
          title="Notifications"
        >
          <Bell className="h-4 w-4" />
          {unreadCount > 0 && (
            <span className="absolute -right-1 -top-1 flex h-4 min-w-[16px] items-center justify-center rounded-full bg-[#9B7AFF] px-1 text-[10px] font-bold text-white">
              {unreadCount}
            </span>
          )}
        </button>

        <button
          onClick={toggleTheme}
          className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--cl-border)] bg-[var(--cl-card)] text-[var(--cl-muted)] transition hover:border-[#9B7AFF]/40 hover:text-[var(--cl-text)]"
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </button>

        <button
          onClick={() => navigate('/settings')}
          className="hidden sm:flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--cl-border)] bg-[var(--cl-card)] text-[var(--cl-muted)] transition hover:border-[#9B7AFF]/40 hover:text-[var(--cl-text)]"
          title="Settings"
        >
          <Settings className="h-4 w-4" />
        </button>

        <button
          onClick={() => navigate('/profile')}
          className="flex h-9 items-center gap-2 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-card)] pl-1.5 pr-2.5 transition hover:border-[#9B7AFF]/40"
          title="Your Profile"
        >
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-gradient-to-br from-[#9B7AFF] to-[#3B82F6] text-[11px] font-bold text-white">
            {profile.avatarInitials || 'AS'}
          </div>
          <span className="hidden lg:inline text-xs font-medium text-[var(--cl-text)]">
            {profile.fullName.split(' ')[0]}
          </span>
        </button>
      </div>
    </header>
  );
}
