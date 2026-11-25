import { Bookmark, Eye, FileText, Info, Sparkles } from 'lucide-react';
import { RiskBadge } from '../common/Badge';

export default function ClauseCard({
  clause,
  personalizedScore,
  onReadFull,
  onViewExplanation,
  onToggleSave,
}) {
  const score = personalizedScore ?? clause.relevanceScore;

  return (
    <div className="glass-card glass-card-hover p-6">
      {/* Header Row */}
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-base font-bold text-[var(--cl-text)]">{clause.title}</h3>
            <RiskBadge level={`${clause.riskLevel} Risk`} />
            <span className="rounded-full border border-[var(--cl-border)] bg-[var(--cl-bg)] px-2.5 py-0.5 text-xs font-medium text-cyan-400">
              {clause.category}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="rounded-xl border border-[#9B7AFF]/35 bg-[#9B7AFF]/10 px-3 py-1.5 text-right">
            <p className="text-[10px] font-medium uppercase tracking-wider text-[var(--cl-muted)]">
              Relevance Score
            </p>
            <p className="text-sm font-extrabold text-[#B79EFF]">{score}/100</p>
          </div>
        </div>
      </div>

      {/* Original Legal Text vs AI-Generated Simple Explanation */}
      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/70 p-4">
          <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[var(--cl-muted)]">
            <FileText className="h-3.5 w-3.5 text-slate-400" />
            Original Legal Text (Verbatim Source)
          </div>
          <p className="font-mono text-xs leading-relaxed text-[var(--cl-muted)]">
            &ldquo;{clause.originalText}&rdquo;
          </p>
        </div>

        <div className="rounded-xl border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 p-4">
          <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-[#B79EFF]">
            <Sparkles className="h-3.5 w-3.5" />
            AI-Generated Simple Explanation
          </div>
          <p className="text-sm leading-relaxed text-[var(--cl-text)]">
            {clause.simpleExplanation}
          </p>
        </div>
      </div>

      {/* Why This Matters To You */}
      <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-500/20 bg-amber-500/10 p-3.5">
        <Info className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
        <div className="text-xs leading-relaxed">
          <span className="font-semibold text-amber-300">Why this matters to you: </span>
          <span className="text-[var(--cl-text)]">{clause.whyItMatters}</span>
        </div>
      </div>

      {/* Actions */}
      <div className="mt-4 flex flex-wrap items-center justify-end gap-2 border-t border-[var(--cl-border)] pt-4">
        <button
          onClick={() => onReadFull(clause)}
          className="cl-btn-secondary px-3 py-1.5 text-xs"
        >
          <FileText className="h-3.5 w-3.5" />
          Read Full Clause
        </button>
        <button
          onClick={() => onViewExplanation(clause)}
          className="cl-btn-secondary px-3 py-1.5 text-xs"
        >
          <Eye className="h-3.5 w-3.5" />
          View Explanation
        </button>
        <button
          onClick={() => onToggleSave(clause.id)}
          className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-semibold transition ${
            clause.saved
              ? 'border-[#9B7AFF] bg-[#9B7AFF]/20 text-[#B79EFF]'
              : 'border-[var(--cl-border)] bg-[var(--cl-elevated)] text-[var(--cl-text)] hover:border-[#9B7AFF]/40'
          }`}
        >
          <Bookmark className={`h-3.5 w-3.5 ${clause.saved ? 'fill-current' : ''}`} />
          {clause.saved ? 'Saved' : 'Save Clause'}
        </button>
      </div>
    </div>
  );
}
