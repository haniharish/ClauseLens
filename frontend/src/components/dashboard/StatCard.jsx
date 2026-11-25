import { ArrowUpRight, AlertCircle } from 'lucide-react';

const ACCENT_MAP = {
  purple: {
    iconBg: 'bg-[#9B7AFF]/15 text-[#9B7AFF] border-[#9B7AFF]/25',
    trend: 'text-emerald-400',
  },
  red: {
    iconBg: 'bg-red-500/15 text-red-400 border-red-500/25',
    trend: 'text-red-400',
  },
  cyan: {
    iconBg: 'bg-cyan-500/15 text-cyan-400 border-cyan-500/25',
    trend: 'text-cyan-400',
  },
  orange: {
    iconBg: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
    trend: 'text-amber-400',
  },
};

export default function StatCard({ label, value, icon: Icon, trend, trendPositive, accent = 'purple', onClick }) {
  const palette = ACCENT_MAP[accent] || ACCENT_MAP.purple;

  return (
    <div
      onClick={onClick}
      className={`glass-card glass-card-hover p-5 ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--cl-muted)]">{label}</p>
          <p className="mt-2 text-3xl font-bold tracking-tight text-[var(--cl-text)]">{value}</p>
        </div>
        <div
          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border ${palette.iconBg}`}
        >
          {Icon && <Icon className="h-5 w-5" />}
        </div>
      </div>

      <div className="mt-4 flex items-center gap-1.5 text-xs font-medium">
        {trendPositive ? (
          <ArrowUpRight className={`h-3.5 w-3.5 ${palette.trend}`} />
        ) : (
          <AlertCircle className={`h-3.5 w-3.5 ${palette.trend}`} />
        )}
        <span className={palette.trend}>{trend}</span>
      </div>
    </div>
  );
}
