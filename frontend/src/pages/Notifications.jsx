import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCheck, Trash2 } from 'lucide-react';
import { useApp } from '../context/AppContext';
import NotificationItem from '../components/notifications/NotificationItem';
import EmptyState from '../components/common/EmptyState';

const FILTERS = [
  { id: 'all', label: 'All' },
  { id: 'unread', label: 'Unread' },
  { id: 'critical', label: 'Critical' },
  { id: 'warning', label: 'Warning' },
  { id: 'info', label: 'Informational' },
];

export default function Notifications() {
  const {
    notifications,
    unreadCount,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    clearAllNotifications,
  } = useApp();
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');

  const filtered = useMemo(() => {
    return notifications.filter((n) => {
      if (filter === 'all') return true;
      if (filter === 'unread') return !n.read;
      return n.severity === filter;
    });
  }, [notifications, filter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Notifications Center
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Real-time policy update alerts, high-risk clause triggers, and analysis completions ({unreadCount} unread).
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={markAllNotificationsRead}
            disabled={unreadCount === 0}
            className="cl-btn-secondary text-xs disabled:opacity-50"
          >
            <CheckCheck className="h-4 w-4 text-emerald-400" />
            Mark all as read
          </button>
          <button
            onClick={clearAllNotifications}
            disabled={notifications.length === 0}
            className="rounded-xl border border-red-500/30 bg-red-500/10 px-3.5 py-2 text-xs font-semibold text-red-400 transition hover:bg-red-500/20 disabled:opacity-50 inline-flex items-center gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear all
          </button>
        </div>
      </div>

      {/* Filter Pills */}
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            onClick={() => setFilter(f.id)}
            className={`rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
              filter === f.id
                ? 'bg-[#9B7AFF] text-white shadow-glow-purple'
                : 'border border-[var(--cl-border)] bg-[var(--cl-card)] text-[var(--cl-muted)] hover:text-[var(--cl-text)]'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Notification List */}
      {filtered.length === 0 ? (
        <EmptyState
          icon={Bell}
          title="You're all caught up"
          description="No notifications match this filter. Policy changes and high-risk alerts will appear here."
        />
      ) : (
        <div className="space-y-3">
          {filtered.map((item) => (
            <NotificationItem
              key={item.id}
              item={item}
              onMarkRead={markNotificationRead}
              onDelete={deleteNotification}
              onNavigate={(n) => {
                markNotificationRead(n.id);
                if (n.link) navigate(n.link);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
