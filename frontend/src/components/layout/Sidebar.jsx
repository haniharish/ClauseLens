import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  FileSearch,
  FolderOpen,
  ShieldAlert,
  Eye,
  GitCompareArrows,
  Bell,
  User,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Scale,
  X,
} from 'lucide-react';
import { useApp } from '../../context/AppContext';

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard },
  { label: 'Analyze Document', to: '/analyze', icon: FileSearch },
  { label: 'My Documents', to: '/documents', icon: FolderOpen },
  { label: 'Risk Analysis', to: '/risk-analysis', icon: ShieldAlert },
  { label: 'Policy Monitoring', to: '/monitoring', icon: Eye },
  { label: 'Version History', to: '/version-history', icon: GitCompareArrows },
  { label: 'Notifications', to: '/notifications', icon: Bell, showBadge: true },
  { label: 'User Profile', to: '/profile', icon: User },
  { label: 'Settings', to: '/settings', icon: Settings },
];

export default function Sidebar({ collapsed, setCollapsed, mobileOpen, setMobileOpen }) {
  const { profile, unreadCount, logout } = useApp();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const sidebarContent = (isMobile = false) => (
    <div className="flex h-full flex-col justify-between bg-[var(--cl-sidebar)] border-r border-[var(--cl-border)] select-none">
      <div>
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-[var(--cl-border)]">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-[#9B7AFF] to-[#06B6D4] shadow-glow-purple">
              <Scale className="h-5 w-5 text-white" />
            </div>
            {(!collapsed || isMobile) && (
              <div className="min-w-0">
                <p className="truncate text-sm font-bold tracking-tight text-[var(--cl-text)]">
                  ClauseLens
                </p>
                <p className="truncate text-[11px] font-medium text-[#9B7AFF]">
                  AI Legal Intelligence
                </p>
              </div>
            )}
          </div>

          {isMobile ? (
            <button
              onClick={() => setMobileOpen(false)}
              className="rounded-lg p-1.5 text-[var(--cl-muted)] hover:bg-white/10"
              aria-label="Close navigation menu"
            >
              <X className="h-5 w-5" />
            </button>
          ) : (
            <button
              onClick={() => setCollapsed(!collapsed)}
              className="hidden lg:flex h-7 w-7 items-center justify-center rounded-lg border border-[var(--cl-border)] text-[var(--cl-muted)] transition hover:border-[#9B7AFF]/50 hover:text-[var(--cl-text)]"
              title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            >
              {collapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </button>
          )}
        </div>

        {/* Navigation Links */}
        <nav className="mt-4 space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => isMobile && setMobileOpen(false)}
                title={collapsed && !isMobile ? item.label : undefined}
                className={({ isActive }) =>
                  `group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-[#9B7AFF]/25 to-[#7C54F5]/10 text-white border border-[#9B7AFF]/40 shadow-[0_4px_16px_-4px_rgba(155,122,255,0.35)]'
                      : 'text-[var(--cl-muted)] hover:bg-white/5 hover:text-[var(--cl-text)] border border-transparent'
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <div className="flex items-center gap-3 min-w-0">
                      <Icon
                        className={`h-4 w-4 shrink-0 transition-colors ${
                          isActive
                            ? 'text-[#9B7AFF]'
                            : 'text-[var(--cl-muted)] group-hover:text-[var(--cl-text)]'
                        }`}
                      />
                      {(!collapsed || isMobile) && (
                        <span className={`truncate ${isActive ? 'text-[var(--cl-text)] font-semibold' : ''}`}>
                          {item.label}
                        </span>
                      )}
                    </div>
                    {item.showBadge && unreadCount > 0 && (!collapsed || isMobile) && (
                      <span className="ml-2 flex h-5 min-w-[20px] items-center justify-center rounded-full bg-[#9B7AFF] px-1.5 text-[11px] font-semibold text-white">
                        {unreadCount}
                      </span>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Bottom User Card & Logout */}
      <div className="border-t border-[var(--cl-border)] p-3">
        <div
          className={`flex items-center gap-3 rounded-xl bg-[var(--cl-card)] p-2.5 border border-[var(--cl-border)] ${
            collapsed && !isMobile ? 'justify-center' : ''
          }`}
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#9B7AFF] to-[#3B82F6] text-xs font-bold text-white">
            {profile.avatarInitials || 'AS'}
          </div>
          {(!collapsed || isMobile) && (
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-[var(--cl-text)]">
                {profile.fullName}
              </p>
              <p className="truncate text-[11px] text-[var(--cl-muted)]">{profile.email}</p>
            </div>
          )}
        </div>

        <button
          onClick={handleLogout}
          className={`mt-2 flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-medium text-red-400 transition hover:bg-red-500/10 ${
            collapsed && !isMobile ? 'justify-center' : ''
          }`}
          title="Logout"
        >
          <LogOut className="h-4 w-4 shrink-0" />
          {(!collapsed || isMobile) && <span>Logout</span>}
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop & Tablet Fixed Sidebar */}
      <aside
        className={`hidden md:block fixed inset-y-0 left-0 z-30 transition-all duration-300 ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        {sidebarContent(false)}
      </aside>

      {/* Mobile Slide-Out Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 md:hidden">
          <div
            className="fixed inset-0 bg-black/65 backdrop-blur-sm"
            onClick={() => setMobileOpen(false)}
          />
          <aside className="fixed inset-y-0 left-0 z-50 w-72 animate-fade-in">
            {sidebarContent(true)}
          </aside>
        </div>
      )}
    </>
  );
}
