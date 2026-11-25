import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  Eye,
  FileText,
  GitCompareArrows,
  Plus,
  Search,
  ShieldAlert,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { DASHBOARD_STATS, RISK_DISTRIBUTION_DATA } from '../data/mockData';
import StatCard from '../components/dashboard/StatCard';
import RiskOverviewCard from '../components/dashboard/RiskOverviewCard';
import RiskDonutChart from '../components/charts/RiskDonutChart';
import RecentDocumentsTable from '../components/dashboard/RecentDocumentsTable';
import RecentPolicyChangesCard from '../components/dashboard/RecentPolicyChangesCard';
import PersonalInsightsCard from '../components/dashboard/PersonalInsightsCard';
import DemoBanner from '../components/common/DemoBanner';

const STAT_ICONS = {
  FileText,
  ShieldAlert,
  Eye,
  GitCompareArrows,
};

export default function Dashboard() {
  const { profile, documents, monitoredPolicies, policyUpdates } = useApp();
  const navigate = useNavigate();

  const [docSearch, setDocSearch] = useState('');
  const [dateRange, setDateRange] = useState('30d');

  const firstName = profile.fullName?.split(' ')[0] || 'Alex';

  const filteredDocuments = useMemo(() => {
    const query = docSearch.trim().toLowerCase();
    return documents
      .filter((doc) => {
        if (!query) return true;
        return (
          doc.name.toLowerCase().includes(query) ||
          doc.type.toLowerCase().includes(query) ||
          doc.riskLevel.toLowerCase().includes(query)
        );
      })
      .slice(0, 6);
  }, [documents, docSearch]);

  // Adjust stats subtly if user adds documents/policies while preserving baseline prompt metrics
  const computedStats = useMemo(() => {
    const extraDocs = Math.max(0, documents.length - 5);
    const extraPolicies = Math.max(0, monitoredPolicies.length - 4);
    return DASHBOARD_STATS.map((stat) => {
      if (stat.id === 'docs_analyzed') {
        return { ...stat, value: stat.value + extraDocs };
      }
      if (stat.id === 'policies_monitored') {
        return { ...stat, value: stat.value + extraPolicies };
      }
      return stat;
    });
  }, [documents.length, monitoredPolicies.length]);

  return (
    <div className="space-y-6">
      {/* Page Header & Top-Right Controls */}
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)] sm:text-3xl">
            Welcome back, {firstName}
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Your personal Terms &amp; Conditions intelligence dashboard.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <div className="relative flex-1 sm:flex-initial">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--cl-muted)]" />
            <input
              type="text"
              value={docSearch}
              onChange={(e) => setDocSearch(e.target.value)}
              placeholder="Search documents..."
              className="cl-input w-full sm:w-52 pl-9 py-2 text-xs"
            />
          </div>

          <div className="relative flex items-center">
            <Calendar className="pointer-events-none absolute left-3 h-3.5 w-3.5 text-[var(--cl-muted)]" />
            <select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="cl-input pl-8 pr-7 py-2 text-xs font-medium cursor-pointer"
              aria-label="Date range filter"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
              <option value="all">All time</option>
            </select>
          </div>

          <button
            onClick={() => navigate('/analyze')}
            className="cl-btn-primary py-2 text-xs sm:text-sm"
          >
            <Plus className="h-4 w-4" />
            Analyze New Document
          </button>
        </div>
      </div>

      <DemoBanner />

      {/* SECTION 1: OVERVIEW STATISTICS */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {computedStats.map((stat) => (
          <StatCard
            key={stat.id}
            label={stat.label}
            value={stat.value}
            icon={STAT_ICONS[stat.icon]}
            trend={stat.trend}
            trendPositive={stat.trendPositive}
            accent={stat.accent}
            onClick={() => {
              if (stat.id === 'docs_analyzed') navigate('/documents');
              if (stat.id === 'high_risk') navigate('/risk-analysis');
              if (stat.id === 'policies_monitored') navigate('/monitoring');
              if (stat.id === 'policy_changes') navigate('/version-history');
            }}
          />
        ))}
      </section>

      {/* SECTION 2 + SECTION 6 (Right Feature Card) & SECTION 3 (Risk Distribution) */}
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="space-y-6 xl:col-span-8">
          <RiskOverviewCard score={72} status="Moderate" />
          <RiskDonutChart data={RISK_DISTRIBUTION_DATA} title="Risk Distribution" />
        </div>

        <div className="space-y-6 xl:col-span-4">
          <PersonalInsightsCard />
          <RecentPolicyChangesCard updates={policyUpdates.slice(0, 3)} />
        </div>
      </section>

      {/* SECTION 4: RECENT DOCUMENT ANALYSIS TABLE */}
      <section>
        <RecentDocumentsTable documents={filteredDocuments} />
      </section>
    </div>
  );
}
