import { AlertTriangle, Bell, Check, Info, ShieldAlert, Trash2 } from 'lucide-react';

const SEVERITY_MAP = {
  critical: {
    container: 'border-l-4 border-l-red-500 bg-red-500/5',
    iconBg: 'bg-red-500/15 text-red-400',
    badge: 'bg-red-500/15 text-red-400 border-red-500/30',
    label: 'Critical',
    Icon: ShieldAlert,
  },
  warning: {
    container: 'border-l-4 border-l-amber-400 bg-amber-500/5',
    iconBg: 'bg-amber-500/15 text-amber-400',
    badge: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    label: 'Warning',
    Icon: AlertTriangle,
  },
  info: {
    container: 'border-l-4 border-l-cyan-400 bg-cyan-500/5',
    iconBg: 'bg-cyan-500/15 text-cyan-400',
    badge: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30',
    label: 'Informational',
    Icon: Info,
  },
};

export default function NotificationItem({ item, onMarkRead, onDelete, onNavigate }) {
  const style = SEVERITY_MAP[item.severity] || SEVERITY_MAP.info;
  const Icon = style.Icon || Bell;

  return (
    <div
      className={`glass-card p-4 sm:p-5 transition-all ${style.container} ${
        item.read ? 'opacity-75' : 'border-[var(--cl-border-light)]'
      }`}
    >
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div
          onClick={() => onNavigate(item)}
          className="flex cursor-pointer items-start gap-3.5 min-w-0"
        >
          <div
            className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${style.iconBg}`}
          >
            <Icon className="h-5 w-5" />
          </div>

          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              {!item.read && (
                <span className="h-2 w-2 rounded-full bg-[#9B7AFF]" title="Unread" />
              )}
              <h3 className="text-sm font-bold text-[var(--cl-text)]">{item.title}</h3>
              <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${style.badge}`}>
                {style.label}
              </span>
              <span className="rounded-md bg-white/5 px-2 py-0.5 text-[11px] text-[var(--cl-muted)]">
                {item.category}
              </span>
            </div>

            <p className="mt-1.5 text-xs leading-relaxed text-[var(--cl-muted)]">
              {item.description}
            </p>
            <p className="mt-2 text-[11px] text-[var(--cl-subtle)]">{item.timestamp}</p>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2 self-end sm:self-center">
          {!item.read && (
            <button
              onClick={() => onMarkRead(item.id)}
              className="cl-btn-secondary px-3 py-1.5 text-xs"
            >
              <Check className="h-3.5 w-3.5 text-emerald-400" />
              Mark as read
            </button>
          )}
          <button
            onClick={() => onDelete(item.id)}
            className="rounded-xl border border-[var(--cl-border)] p-2 text-[var(--cl-muted)] transition hover:border-red-500/40 hover:bg-red-500/10 hover:text-red-400"
            title="Clear notification"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
