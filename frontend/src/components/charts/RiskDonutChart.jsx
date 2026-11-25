import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

export default function RiskDonutChart({ data = [], title = 'Risk Distribution' }) {
  const total = data.reduce((sum, d) => sum + d.value, 0) || 1;

  return (
    <div className="glass-card glass-card-hover flex h-full flex-col p-6">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">{title}</h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            Breakdown of detected risk categories
          </p>
        </div>
        <span className="rounded-lg border border-[var(--cl-border)] bg-[var(--cl-bg)] px-2.5 py-1 text-[11px] font-medium text-[#9B7AFF]">
          {data.length} Categories
        </span>
      </div>

      <div className="grid flex-1 grid-cols-1 items-center gap-4 sm:grid-cols-12">
        <div className="h-56 sm:col-span-6">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={52}
                outerRadius={82}
                paddingAngle={3}
                stroke="none"
              >
                {data.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value, name) => [`${Math.round((value / total) * 100)}%`, name]}
                contentStyle={{
                  backgroundColor: '#0D0F19',
                  borderColor: 'rgba(155, 122, 255, 0.35)',
                  borderRadius: '0.75rem',
                  fontSize: '12px',
                  color: '#F1F5F9',
                }}
                itemStyle={{ color: '#F1F5F9' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-2.5 sm:col-span-6">
          {data.map((item) => {
            const pct = Math.round((item.value / total) * 100);
            return (
              <div
                key={item.name}
                className="flex items-center justify-between rounded-lg px-2 py-1 text-xs transition hover:bg-white/5"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <span
                    className="h-2.5 w-2.5 shrink-0 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <span className="truncate text-[var(--cl-text)]">{item.name}</span>
                </div>
                <span className="ml-2 font-semibold text-[var(--cl-muted)]">{pct}%</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
