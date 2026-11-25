import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  AlertTriangle,
  ArrowRight,
  GitCompareArrows,
  Info,
  Sparkles,
} from 'lucide-react';
import { VERSION_COMPARISONS } from '../data/mockData';
import { ChangeTypeBadge, RiskBadge } from '../components/common/Badge';
import DemoBanner from '../components/common/DemoBanner';

const CHANGE_CATEGORIES = ['All', 'Added', 'Modified', 'Removed', 'Unchanged'];

const DIRECTION_STYLES = {
  'Less favorable': 'bg-red-500/15 text-red-400 border-red-500/30',
  Neutral: 'bg-slate-500/15 text-slate-300 border-slate-500/30',
  'More favorable': 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  Unclear: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
};

export default function VersionHistory() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialId = searchParams.get('id') || VERSION_COMPARISONS[0].id;
  const [selectedId, setSelectedId] = useState(
    VERSION_COMPARISONS.some((v) => v.id === initialId) ? initialId : VERSION_COMPARISONS[0].id
  );
  const [categoryFilter, setCategoryFilter] = useState('All');

  const activeComparison = useMemo(
    () => VERSION_COMPARISONS.find((v) => v.id === selectedId) || VERSION_COMPARISONS[0],
    [selectedId]
  );

  const visibleDiffs = useMemo(() => {
    if (categoryFilter === 'All') return activeComparison.diffs;
    return activeComparison.diffs.filter((d) => d.category === categoryFilter);
  }, [activeComparison, categoryFilter]);

  const handleSelectPolicy = (id) => {
    setSelectedId(id);
    setCategoryFilter('All');
    setSearchParams({ id });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Policy Version History
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Side-by-side policy diff with AI-assisted change summarization and personal impact scoring.
          </p>
        </div>

        <select
          value={selectedId}
          onChange={(e) => handleSelectPolicy(e.target.value)}
          className="cl-input w-full sm:w-72 text-xs font-semibold cursor-pointer"
          aria-label="Select policy comparison"
        >
          {VERSION_COMPARISONS.map((v) => (
            <option key={v.id} value={v.id}>
              {v.service} ({v.previousVersion} → {v.currentVersion})
            </option>
          ))}
        </select>
      </div>

      <DemoBanner />

      {/* Version Metadata Bar */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="glass-card p-4">
          <p className="text-xs text-[var(--cl-muted)]">Previous Version</p>
          <p className="mt-1 font-mono text-sm font-bold text-[var(--cl-text)]">
            {activeComparison.previousVersion}
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-[var(--cl-muted)]">Current Version</p>
          <p className="mt-1 font-mono text-sm font-bold text-[#9B7AFF]">
            {activeComparison.currentVersion}
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-[var(--cl-muted)]">Last Updated Date</p>
          <p className="mt-1 text-sm font-bold text-[var(--cl-text)]">
            {activeComparison.lastUpdated}
          </p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs text-[var(--cl-muted)]">Changes Detected</p>
          <p className="mt-1 text-sm font-bold text-amber-400">
            {activeComparison.changesDetected} clauses modified/added
          </p>
        </div>
      </div>

      {/* AI Change Summary Card */}
      <div className="glass-card border border-[#9B7AFF]/35 bg-gradient-to-br from-[#9B7AFF]/10 via-[var(--cl-card)] to-cyan-500/5 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#9B7AFF]/20 text-[#9B7AFF]">
              <Sparkles className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-[var(--cl-text)]">AI Change Summary</h2>
              <p className="text-xs text-[var(--cl-muted)]">
                Automated semantic diff summary for {activeComparison.service}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                DIRECTION_STYLES[activeComparison.changeDirection] || DIRECTION_STYLES.Unclear
              }`}
            >
              Direction: {activeComparison.changeDirection}
            </span>
            <RiskBadge level={`${activeComparison.impactLevel} Impact`} />
            <span className="rounded-full border border-[#9B7AFF]/40 bg-[#9B7AFF]/15 px-3 py-1 text-xs font-bold text-[#B79EFF]">
              Personalized Alert Score: {activeComparison.personalizedAlertScore}/100
            </span>
          </div>
        </div>

        <p className="mt-4 text-sm leading-relaxed text-[var(--cl-text)]">
          {activeComparison.aiSummary}
        </p>

        <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-500/25 bg-amber-500/10 p-3.5 text-xs">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
          <div>
            <span className="font-semibold text-amber-300">Why this change matters: </span>
            <span className="text-[var(--cl-text)]">{activeComparison.whyItMatters}</span>
          </div>
        </div>
      </div>

      {/* Category Filter + Color Legend + Show All Changes */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {CHANGE_CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                categoryFilter === cat
                  ? 'bg-[#9B7AFF] text-white shadow-glow-purple'
                  : 'border border-[var(--cl-border)] bg-[var(--cl-card)] text-[var(--cl-muted)] hover:text-[var(--cl-text)]'
              }`}
            >
              {cat === 'All' ? 'Show All Changes' : cat}
            </button>
          ))}
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs text-[var(--cl-muted)]">
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-emerald-500" /> Added
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-red-500" /> Removed
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-sm bg-amber-400" /> Modified
          </span>
        </div>
      </div>

      {/* Two-Panel Old vs New Comparison */}
      <div className="space-y-4">
        {visibleDiffs.map((diff) => {
          const oldHighlight =
            diff.category === 'Removed'
              ? 'border-red-500/40 bg-red-500/10 text-red-200'
              : diff.category === 'Modified'
              ? 'border-amber-500/35 bg-amber-500/10 text-[var(--cl-text)]'
              : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-[var(--cl-muted)]';

          const newHighlight =
            diff.category === 'Added'
              ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200'
              : diff.category === 'Modified'
              ? 'border-amber-500/40 bg-amber-500/15 text-[var(--cl-text)]'
              : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-[var(--cl-muted)]';

          return (
            <div key={diff.id} className="glass-card p-5">
              <div className="mb-4 flex flex-wrap items-center justify-between gap-2 border-b border-[var(--cl-border)] pb-3">
                <div className="flex items-center gap-2">
                  <GitCompareArrows className="h-4 w-4 text-[#9B7AFF]" />
                  <h3 className="text-sm font-bold text-[var(--cl-text)]">{diff.section}</h3>
                </div>
                <ChangeTypeBadge type={diff.category} />
              </div>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                {/* LEFT: Old Policy Text */}
                <div className={`rounded-xl border p-4 ${oldHighlight}`}>
                  <p className="mb-2 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-[var(--cl-muted)]">
                    <span>Old Policy Text</span>
                    <span>{activeComparison.previousVersion}</span>
                  </p>
                  {diff.oldText ? (
                    <p className="text-xs leading-relaxed">{diff.oldText}</p>
                  ) : (
                    <p className="flex items-center gap-1.5 text-xs italic text-[var(--cl-muted)]">
                      <Info className="h-3.5 w-3.5" />
                      Clause did not exist in the previous version.
                    </p>
                  )}
                </div>

                {/* RIGHT: New Policy Text */}
                <div className={`rounded-xl border p-4 ${newHighlight}`}>
                  <p className="mb-2 flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-[var(--cl-muted)]">
                    <span className="inline-flex items-center gap-1">
                      <ArrowRight className="h-3 w-3 text-[#9B7AFF]" />
                      New Policy Text
                    </span>
                    <span>{activeComparison.currentVersion}</span>
                  </p>
                  {diff.newText ? (
                    <p className="text-xs leading-relaxed">{diff.newText}</p>
                  ) : (
                    <p className="flex items-center gap-1.5 text-xs italic text-red-400">
                      <Info className="h-3.5 w-3.5" />
                      This clause was removed in the current version.
                    </p>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
