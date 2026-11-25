import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, ArrowUpRight, ShieldAlert, Users } from 'lucide-react';
import { useApp } from '../context/AppContext';
import {
  PERSONA_COMPARISON_DATA,
  RISK_DISTRIBUTION_DATA,
  RISK_TREND_DATA,
} from '../data/mockData';
import RiskDonutChart from '../components/charts/RiskDonutChart';
import RiskTrendChart from '../components/charts/RiskTrendChart';
import { RiskBadge } from '../components/common/Badge';
import DemoBanner from '../components/common/DemoBanner';
import { computePersonalizedScore } from '../utils/helpers';

export default function RiskAnalysis() {
  const { documents, profile } = useApp();
  const navigate = useNavigate();
  const [selectedPersona, setSelectedPersona] = useState('Students');

  const allClauses = useMemo(() => {
    return documents.flatMap((doc) =>
      (doc.clauses || []).map((c) => ({
        ...c,
        docId: doc.id,
        docName: doc.name,
        personalizedScore: computePersonalizedScore(c.relevanceScore, c.category, profile),
      }))
    );
  }, [documents, profile]);

  const criticalClauses = useMemo(() => {
    return [...allClauses]
      .sort((a, b) => b.personalizedScore - a.personalizedScore)
      .slice(0, 5);
  }, [allClauses]);

  const categoryBreakdown = useMemo(() => {
    return RISK_DISTRIBUTION_DATA.map((cat) => ({
      ...cat,
      count: allClauses.filter((c) => c.category === cat.name).length,
    }));
  }, [allClauses]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Personalized Risk Analysis
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Deep analytics across risk categories, trend trajectory, and user-role relevance.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-xl border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 px-3.5 py-2 text-xs">
          <span className="text-[var(--cl-muted)]">Overall Risk Score:</span>
          <span className="text-base font-bold text-[#9B7AFF]">72/100</span>
        </div>
      </div>

      <DemoBanner />

      {/* Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <RiskDonutChart data={RISK_DISTRIBUTION_DATA} title="Risk Distribution" />
        <RiskTrendChart data={RISK_TREND_DATA} />
      </div>

      {/* Category Breakdown & Personalized Ranking */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="glass-card p-6 lg:col-span-5">
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">Risk Category Breakdown</h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            Proportion and clause concentration by legal topic
          </p>
          <div className="mt-5 space-y-4">
            {categoryBreakdown.map((cat) => (
              <div key={cat.name}>
                <div className="mb-1.5 flex items-center justify-between text-xs">
                  <span className="font-medium text-[var(--cl-text)]">{cat.name}</span>
                  <span className="text-[var(--cl-muted)]">
                    {cat.value}% weight · {cat.count} sample clauses
                  </span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--cl-bg)]">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${cat.value * 3}%`, backgroundColor: cat.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6 lg:col-span-7">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-[var(--cl-text)]">
                Most Critical Clauses (Personalized Ranking)
              </h2>
              <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
                Ranked for your {profile.intendedUse?.join(', ')} ({profile.jurisdiction}) profile
              </p>
            </div>
            <ShieldAlert className="h-5 w-5 text-red-400" />
          </div>

          <div className="space-y-3">
            {criticalClauses.map((clause, index) => (
              <div
                key={clause.id}
                onClick={() => navigate(`/analysis/${clause.docId}`)}
                className="flex cursor-pointer items-center justify-between gap-4 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/55 p-3.5 transition hover:border-[#9B7AFF]/40"
              >
                <div className="flex items-start gap-3 min-w-0">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-[#9B7AFF]/15 text-xs font-bold text-[#9B7AFF]">
                    #{index + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="truncate text-sm font-semibold text-[var(--cl-text)]">
                        {clause.title}
                      </p>
                      <RiskBadge level={clause.riskLevel} />
                    </div>
                    <p className="mt-0.5 truncate text-xs text-[var(--cl-muted)]">
                      {clause.docName} · {clause.category}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="rounded-lg bg-red-500/15 px-2.5 py-1 text-xs font-bold text-red-400">
                    {clause.personalizedScore}/100
                  </span>
                  <ArrowUpRight className="h-4 w-4 text-[var(--cl-muted)]" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Why These Clauses Matter to You — Persona Comparison */}
      <section className="glass-card p-6">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-[var(--cl-text)]">
              Why These Clauses Matter to You
            </h2>
            <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
              See how the exact same legal clause carries different relevance scores depending on user role
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {PERSONA_COMPARISON_DATA.map((p) => (
              <button
                key={p.persona}
                onClick={() => setSelectedPersona(p.persona)}
                className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                  selectedPersona === p.persona
                    ? 'bg-[#9B7AFF] text-white shadow-glow-purple'
                    : 'border border-[var(--cl-border)] bg-[var(--cl-bg)] text-[var(--cl-muted)] hover:text-[var(--cl-text)]'
                }`}
              >
                {p.persona}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {PERSONA_COMPARISON_DATA.map((item) => {
            const isSelected = selectedPersona === item.persona;
            return (
              <div
                key={item.persona}
                onClick={() => setSelectedPersona(item.persona)}
                className={`cursor-pointer rounded-2xl border p-5 transition-all ${
                  isSelected
                    ? 'border-[#9B7AFF] bg-[#9B7AFF]/10 shadow-glow-purple'
                    : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/55 hover:border-[#9B7AFF]/35'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4" style={{ color: item.color }} />
                    <h3 className="text-sm font-bold text-[var(--cl-text)]">{item.persona}</h3>
                  </div>
                  <span
                    className="rounded-full px-2.5 py-0.5 text-xs font-bold"
                    style={{
                      backgroundColor: `${item.color}22`,
                      color: item.color,
                    }}
                  >
                    {item.avgRelevance}/100
                  </span>
                </div>

                <p className="mt-3 text-xs leading-relaxed text-[var(--cl-muted)]">
                  {item.keyConcern}
                </p>

                <div className="mt-3 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-card)] p-2.5">
                  <p className="flex items-center gap-1 text-[11px] font-semibold text-amber-400">
                    <AlertTriangle className="h-3 w-3" />
                    High-Impact Example
                  </p>
                  <p className="mt-1 text-[11px] text-[var(--cl-muted)]">{item.exampleClause}</p>
                </div>

                <div className="mt-3 flex flex-wrap gap-1.5">
                  {item.topCategories.map((cat) => (
                    <span
                      key={cat}
                      className="rounded-md bg-white/5 px-2 py-0.5 text-[10px] font-medium text-[var(--cl-muted)]"
                    >
                      {cat}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
