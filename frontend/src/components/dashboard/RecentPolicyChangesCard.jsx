import { useNavigate } from 'react-router-dom';
import { GitCompareArrows, ArrowRight } from 'lucide-react';
import { ChangeTypeBadge, RiskBadge } from '../common/Badge';

export default function RecentPolicyChangesCard({ updates = [] }) {
  const navigate = useNavigate();

  return (
    <div className="glass-card glass-card-hover p-6">
      <div className="mb-4 flex items-center justify-between gap-2">
        <div>
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">Recent Policy Changes</h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            Version-diff alerts from your monitored services
          </p>
        </div>
        <button
          onClick={() => navigate('/version-history')}
          className="inline-flex items-center gap-1 text-xs font-semibold text-[#9B7AFF] hover:underline"
        >
          Compare all
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="space-y-3">
        {updates.map((upd) => (
          <div
            key={upd.id}
            className="flex flex-col justify-between gap-3 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/55 p-4 transition hover:border-[#9B7AFF]/35 sm:flex-row sm:items-center"
          >
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400">
                <GitCompareArrows className="h-4 w-4" />
              </div>
              <div>
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="text-sm font-semibold text-[var(--cl-text)]">
                    {upd.documentName}
                  </h3>
                  <ChangeTypeBadge type={upd.changeType} />
                  <RiskBadge level={`${upd.riskImpact} Impact`} />
                </div>
                <p className="mt-1 text-xs font-medium text-[var(--cl-text)]">{upd.summary}</p>
                <p className="mt-0.5 text-[11px] text-[var(--cl-muted)]">
                  {upd.detail} · Detected {upd.dateDetected}
                </p>
              </div>
            </div>

            <button
              onClick={() => navigate(`/version-history?id=${upd.versionRef}`)}
              className="cl-btn-secondary shrink-0 px-3.5 py-2 text-xs"
            >
              View Changes
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
