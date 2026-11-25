import { getRiskStyles } from '../../utils/helpers';

export function RiskBadge({ level, className = '' }) {
  const styles = getRiskStyles(level);
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${styles.badge} ${className}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${styles.dot}`} />
      {level}
    </span>
  );
}

export function ChangeTypeBadge({ type }) {
  const map = {
    Added: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    Modified: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    Removed: 'bg-red-500/15 text-red-400 border-red-500/30',
    Unchanged: 'bg-slate-500/15 text-slate-400 border-slate-500/30',
  };
  const cls = map[type] || map.Unchanged;
  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${cls}`}>
      {type}
    </span>
  );
}
