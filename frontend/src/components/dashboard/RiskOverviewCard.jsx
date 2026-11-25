import { ShieldCheck } from 'lucide-react';

export default function RiskOverviewCard({
  score = 72,
  status = 'Moderate',
  highCount = 18,
  mediumCount = 70,
  lowCount = 73,
}) {
  const total = Math.max(1, highCount + mediumCount + lowCount);
  const categories = [
    {
      label: 'High Risk',
      count: highCount,
      pct: Math.round((highCount / total) * 100),
      barClass: 'from-red-500 to-rose-400',
      textClass: 'text-red-400',
    },
    {
      label: 'Medium Risk',
      count: mediumCount,
      pct: Math.round((mediumCount / total) * 100),
      barClass: 'from-amber-500 to-orange-400',
      textClass: 'text-amber-400',
    },
    {
      label: 'Low Risk',
      count: lowCount,
      pct: Math.round((lowCount / total) * 100),
      barClass: 'from-emerald-500 to-cyan-400',
      textClass: 'text-emerald-400',
    },
  ];

  // SVG circular gauge math
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="glass-card glass-card-hover p-6">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">Your Risk Overview</h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            Aggregated across all analyzed Terms &amp; Privacy Policies
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/15 px-3 py-1 text-xs font-semibold text-amber-400">
          <ShieldCheck className="h-3.5 w-3.5" />
          {status} Risk
        </span>
      </div>

      <div className="grid grid-cols-1 items-center gap-6 sm:grid-cols-12">
        {/* Circular Progress Indicator */}
        <div className="flex flex-col items-center justify-center sm:col-span-4">
          <div className="relative flex h-36 w-36 items-center justify-center">
            <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 132 132">
              <defs>
                <linearGradient id="riskRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#9B7AFF" />
                  <stop offset="55%" stopColor="#F59E0B" />
                  <stop offset="100%" stopColor="#06B6D4" />
                </linearGradient>
              </defs>
              <circle
                cx="66"
                cy="66"
                r={radius}
                stroke="rgba(148,163,184,0.14)"
                strokeWidth="11"
                fill="none"
              />
              <circle
                cx="66"
                cy="66"
                r={radius}
                stroke="url(#riskRingGrad)"
                strokeWidth="11"
                strokeLinecap="round"
                fill="none"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                className="transition-all duration-700 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-3xl font-extrabold text-[var(--cl-text)]">{score}</span>
              <span className="text-[11px] font-medium text-[var(--cl-muted)]">out of 100</span>
            </div>
          </div>
          <span className="mt-2 text-xs font-medium text-amber-400">
            Status: {status}
          </span>
        </div>

        {/* Explanation + Category Bars */}
        <div className="space-y-4 sm:col-span-8">
          <p className="rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/60 p-3.5 text-xs leading-relaxed text-[var(--cl-muted)]">
            Your analyzed policies contain clauses that may affect your personal data, account
            rights and subscription conditions.
          </p>

          <div className="space-y-3">
            {categories.map((cat) => (
              <div key={cat.label}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <span className="font-medium text-[var(--cl-text)]">{cat.label}</span>
                  <span className={`font-semibold ${cat.textClass}`}>
                    {cat.count} clauses ({cat.pct}%)
                  </span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--cl-bg)]">
                  <div
                    className={`h-full rounded-full bg-gradient-to-r ${cat.barClass} transition-all duration-500`}
                    style={{ width: `${cat.pct}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
