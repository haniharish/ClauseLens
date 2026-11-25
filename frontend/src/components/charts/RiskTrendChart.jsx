import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

export default function RiskTrendChart({ data = [] }) {
  return (
    <div className="glass-card glass-card-hover p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">Risk Score Trend</h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            6-month evolution of personalized risk exposure across tracked policies
          </p>
        </div>
        <span className="rounded-lg border border-[var(--cl-border)] bg-[var(--cl-bg)] px-2.5 py-1 text-[11px] font-medium text-cyan-400">
          Last 6 Months
        </span>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 12, left: -16, bottom: 0 }}>
            <defs>
              <linearGradient id="riskTrendFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#9B7AFF" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#9B7AFF" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.12)" />
            <XAxis
              dataKey="month"
              stroke="#64748B"
              tick={{ fill: '#94A3B8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis
              domain={[30, 100]}
              stroke="#64748B"
              tick={{ fill: '#94A3B8', fontSize: 12 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#0D0F19',
                borderColor: 'rgba(155, 122, 255, 0.35)',
                borderRadius: '0.75rem',
                fontSize: '12px',
                color: '#F1F5F9',
              }}
            />
            <Area
              type="monotone"
              dataKey="riskScore"
              name="Avg Risk Score"
              stroke="#9B7AFF"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#riskTrendFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
