import { useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Search, ShieldAlert, Sparkles } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';
import ClauseCard from '../components/analysis/ClauseCard';
import { RiskBadge } from '../components/common/Badge';
import Modal from '../components/common/Modal';
import EmptyState from '../components/common/EmptyState';
import DemoBanner from '../components/common/DemoBanner';
import { computePersonalizedScore, getScoreLabel } from '../utils/helpers';

const CATEGORIES = [
  'All',
  'Data Sharing',
  'Data Collection',
  'Arbitration',
  'Auto-Renewal & Fees',
  'Account Termination',
  'Other Clauses',
];

const RISK_ORDER = { High: 3, Medium: 2, Low: 1 };

export default function AnalysisResults() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { documents, profile, toggleSaveClause } = useApp();

  const doc = useMemo(
    () => documents.find((d) => d.id === id) || documents[0],
    [documents, id]
  );

  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [sortBy, setSortBy] = useState('risk');
  const [modalState, setModalState] = useState({ open: false, mode: 'full', clause: null });

  const filteredClauses = useMemo(() => {
    if (!doc?.clauses) return [];
    const q = search.trim().toLowerCase();
    return doc.clauses
      .map((c) => ({
        ...c,
        personalizedScore: computePersonalizedScore(c.relevanceScore, c.category, profile),
      }))
      .filter((c) => {
        if (categoryFilter !== 'All' && c.category !== categoryFilter) return false;
        if (!q) return true;
        return (
          c.title.toLowerCase().includes(q) ||
          c.originalText.toLowerCase().includes(q) ||
          c.simpleExplanation.toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        if (sortBy === 'risk') {
          return (RISK_ORDER[b.riskLevel] || 0) - (RISK_ORDER[a.riskLevel] || 0);
        }
        return b.personalizedScore - a.personalizedScore;
      });
  }, [doc, search, categoryFilter, sortBy, profile]);

  if (!doc) {
    return (
      <EmptyState
        icon={ShieldAlert}
        title="No analysis selected"
        description="Upload or select a policy document to inspect AI clause summaries."
        action={
          <button onClick={() => navigate('/analyze')} className="cl-btn-primary">
            Analyze a Document
          </button>
        }
      />
    );
  }

  const counts = doc.summaryCounts || {
    high: doc.clauses?.filter((c) => c.riskLevel === 'High').length || 0,
    medium: doc.clauses?.filter((c) => c.riskLevel === 'Medium').length || 0,
    low: doc.clauses?.filter((c) => c.riskLevel === 'Low').length || 0,
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="mb-2 inline-flex items-center gap-1.5 text-xs font-medium text-[var(--cl-muted)] hover:text-[var(--cl-text)]"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            Back
          </button>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Document Analysis Results
          </h1>
          <div className="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-[var(--cl-muted)]">
            <span className="font-semibold text-[var(--cl-text)]">{doc.name}</span>
            <span>·</span>
            <span>Uploaded {doc.dateAnalyzed}</span>
            <span>·</span>
            <span>{doc.clausesFound} clauses detected</span>
            <span>·</span>
            <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-[11px] font-semibold text-emerald-400">
              {doc.status}
            </span>
          </div>
        </div>
      </div>

      <DemoBanner />

      {/* Overall Risk Summary */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div className="glass-card p-5 lg:col-span-2 flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-[var(--cl-muted)]">Overall Risk Score</p>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-[var(--cl-text)]">
                {doc.riskScore}
              </span>
              <span className="text-xs text-[var(--cl-muted)]">/ 100</span>
            </div>
            <div className="mt-2">
              <RiskBadge level={getScoreLabel(doc.riskScore)} />
            </div>
          </div>
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#9B7AFF]/15 text-[#9B7AFF]">
            <Sparkles className="h-7 w-7" />
          </div>
        </div>

        <div className="glass-card p-5">
          <p className="text-xs font-medium text-[var(--cl-muted)]">High-Risk Clauses</p>
          <p className="mt-2 text-2xl font-bold text-red-400">{counts.high}</p>
          <p className="mt-1 text-[11px] text-[var(--cl-muted)]">Immediate review advised</p>
        </div>

        <div className="glass-card p-5">
          <p className="text-xs font-medium text-[var(--cl-muted)]">Medium-Risk Clauses</p>
          <p className="mt-2 text-2xl font-bold text-amber-400">{counts.medium}</p>
          <p className="mt-1 text-[11px] text-[var(--cl-muted)]">Conditional obligations</p>
        </div>

        <div className="glass-card p-5">
          <p className="text-xs font-medium text-[var(--cl-muted)]">Low-Risk Clauses</p>
          <p className="mt-2 text-2xl font-bold text-emerald-400">{counts.low}</p>
          <p className="mt-1 text-[11px] text-[var(--cl-muted)]">Standard terms</p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="glass-card flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--cl-muted)]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search extracted clauses or keywords..."
            className="cl-input pl-10 text-xs"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="cl-input w-auto text-xs cursor-pointer"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat === 'All' ? 'All Categories' : cat}
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="cl-input w-auto text-xs cursor-pointer"
          >
            <option value="risk">Sort by Risk Level</option>
            <option value="relevance">Sort by Relevance Score</option>
          </select>
        </div>
      </div>

      {/* Clause List */}
      <div className="space-y-4">
        {filteredClauses.length === 0 ? (
          <EmptyState
            icon={Search}
            title="No matching clauses"
            description="Try clearing your search query or switching the risk category filter."
          />
        ) : (
          filteredClauses.map((clause) => (
            <ClauseCard
              key={clause.id}
              clause={clause}
              personalizedScore={clause.personalizedScore}
              onReadFull={(c) => setModalState({ open: true, mode: 'full', clause: c })}
              onViewExplanation={(c) =>
                setModalState({ open: true, mode: 'explanation', clause: c })
              }
              onToggleSave={(clauseId) => {
                toggleSaveClause(doc.id, clauseId);
                toast.success(clause.saved ? 'Removed from saved clauses' : 'Clause saved');
              }}
            />
          ))
        )}
      </div>

      {/* Modal for Full Clause / Detailed AI Explanation */}
      <Modal
        isOpen={modalState.open}
        onClose={() => setModalState({ open: false, mode: 'full', clause: null })}
        title={modalState.clause?.title}
        subtitle={
          modalState.mode === 'full'
            ? 'Verbatim Original Legal Clause'
            : 'AI Plain-Language Breakdown & Personal Context'
        }
      >
        {modalState.clause && (
          <div className="space-y-4 text-sm">
            {modalState.mode === 'full' ? (
              <div className="rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)] p-4 font-mono text-xs leading-relaxed text-[var(--cl-muted)]">
                {modalState.clause.originalText}
              </div>
            ) : (
              <>
                <div className="rounded-xl border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 p-4">
                  <p className="mb-1 text-xs font-semibold text-[#B79EFF]">
                    AI-Generated Simple Explanation
                  </p>
                  <p className="leading-relaxed text-[var(--cl-text)]">
                    {modalState.clause.simpleExplanation}
                  </p>
                </div>
                <div className="rounded-xl border border-amber-500/25 bg-amber-500/10 p-4">
                  <p className="mb-1 text-xs font-semibold text-amber-300">
                    Personalized Impact ({profile.intendedUse?.join(', ')} · {profile.jurisdiction})
                  </p>
                  <p className="text-xs leading-relaxed text-[var(--cl-text)]">
                    {modalState.clause.whyItMatters}
                  </p>
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
