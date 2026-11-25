import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  FolderOpen,
  LayoutGrid,
  List,
  Plus,
  RefreshCw,
  Search,
  Trash2,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { RiskBadge } from '../components/common/Badge';
import EmptyState from '../components/common/EmptyState';

export default function MyDocuments() {
  const { documents, deleteDocument, reanalyzeDocument, globalSearch } = useApp();
  const navigate = useNavigate();

  const [search, setSearch] = useState(globalSearch || '');
  const [typeFilter, setTypeFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [sortBy, setSortBy] = useState('newest');
  const [viewMode, setViewMode] = useState('grid');

  const filteredDocs = useMemo(() => {
    const q = (search || globalSearch || '').trim().toLowerCase();
    return [...documents]
      .filter((d) => {
        if (typeFilter !== 'All' && d.type !== typeFilter) return false;
        if (riskFilter !== 'All' && d.riskLevel !== riskFilter) return false;
        if (!q) return true;
        return d.name.toLowerCase().includes(q) || d.type.toLowerCase().includes(q);
      })
      .sort((a, b) => {
        if (sortBy === 'newest') return b.dateAnalyzed.localeCompare(a.dateAnalyzed);
        if (sortBy === 'oldest') return a.dateAnalyzed.localeCompare(b.dateAnalyzed);
        return b.riskScore - a.riskScore;
      });
  }, [documents, search, globalSearch, typeFilter, riskFilter, sortBy]);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">My Documents</h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Manage analyzed Terms &amp; Conditions, Privacy Policies, and PDF reports.
          </p>
        </div>
        <button onClick={() => navigate('/analyze')} className="cl-btn-primary">
          <Plus className="h-4 w-4" />
          Upload New Document
        </button>
      </div>

      {/* Controls Bar */}
      <div className="glass-card flex flex-col gap-3 p-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--cl-muted)]" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents by name or type..."
            className="cl-input pl-10 text-xs"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="cl-input w-auto text-xs cursor-pointer"
          >
            <option value="All">All Types</option>
            <option value="Privacy Policy">Privacy Policy</option>
            <option value="Terms & Conditions">Terms &amp; Conditions</option>
            <option value="User Agreement">User Agreement</option>
            <option value="Services Agreement">Services Agreement</option>
          </select>

          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="cl-input w-auto text-xs cursor-pointer"
          >
            <option value="All">All Risk Levels</option>
            <option value="High Risk">High Risk</option>
            <option value="Medium Risk">Medium Risk</option>
            <option value="Low Risk">Low Risk</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="cl-input w-auto text-xs cursor-pointer"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="risk">Highest Risk Score</option>
          </select>

          <div className="flex rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)] p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`rounded-lg p-1.5 transition ${
                viewMode === 'grid'
                  ? 'bg-[#9B7AFF] text-white'
                  : 'text-[var(--cl-muted)] hover:text-[var(--cl-text)]'
              }`}
              title="Grid view"
            >
              <LayoutGrid className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`rounded-lg p-1.5 transition ${
                viewMode === 'table'
                  ? 'bg-[#9B7AFF] text-white'
                  : 'text-[var(--cl-muted)] hover:text-[var(--cl-text)]'
              }`}
              title="Table view"
            >
              <List className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Documents List */}
      {filteredDocs.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title="No documents found"
          description="No uploaded or analyzed documents match your filters. Upload a PDF or analyze a policy URL to get started."
          action={
            <button onClick={() => navigate('/analyze')} className="cl-btn-primary">
              <Plus className="h-4 w-4" />
              Analyze Document
            </button>
          }
        />
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredDocs.map((doc) => (
            <div key={doc.id} className="glass-card glass-card-hover flex flex-col justify-between p-5">
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#9B7AFF]/15 text-[#9B7AFF]">
                      <FileText className="h-5 w-5" />
                    </div>
                    <div className="min-w-0">
                      <h3 className="truncate text-sm font-bold text-[var(--cl-text)]">
                        {doc.name}
                      </h3>
                      <p className="text-xs text-[var(--cl-muted)]">
                        {doc.type} · {doc.fileType}
                      </p>
                    </div>
                  </div>
                  <RiskBadge level={doc.riskLevel} />
                </div>

                <div className="mt-4 grid grid-cols-3 gap-2 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/55 p-3 text-center">
                  <div>
                    <p className="text-[10px] text-[var(--cl-muted)]">Clauses</p>
                    <p className="mt-0.5 text-sm font-bold text-[var(--cl-text)]">
                      {doc.clausesFound}
                    </p>
                  </div>
                  <div>
                    <p className="text-[10px] text-[var(--cl-muted)]">Risk Score</p>
                    <p className="mt-0.5 text-sm font-bold text-[#9B7AFF]">{doc.riskScore}/100</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-[var(--cl-muted)]">Status</p>
                    <p className="mt-0.5 text-xs font-semibold text-emerald-400">{doc.status}</p>
                  </div>
                </div>
                <p className="mt-3 text-[11px] text-[var(--cl-muted)]">
                  Uploaded on {doc.dateAnalyzed} · Size: {doc.fileSize}
                </p>
              </div>

              <div className="mt-4 flex items-center justify-between gap-2 border-t border-[var(--cl-border)] pt-3">
                <button
                  onClick={() => navigate(`/analysis/${doc.id}`)}
                  className="cl-btn-primary flex-1 py-2 text-xs"
                >
                  View
                </button>
                <button
                  onClick={() => reanalyzeDocument(doc.id)}
                  className="cl-btn-secondary px-3 py-2 text-xs"
                  title="Re-analyze"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                </button>
                <button
                  onClick={() => deleteDocument(doc.id)}
                  className="rounded-xl border border-red-500/25 bg-red-500/10 p-2 text-red-400 transition hover:bg-red-500/20"
                  title="Delete"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-card overflow-x-auto">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr className="border-b border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-xs font-semibold uppercase text-[var(--cl-muted)]">
                <th className="px-5 py-3.5">Document Name</th>
                <th className="px-4 py-3.5">File Type</th>
                <th className="px-4 py-3.5">Upload Date</th>
                <th className="px-4 py-3.5">Clauses</th>
                <th className="px-4 py-3.5">Risk Score</th>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-5 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--cl-border)]">
              {filteredDocs.map((doc) => (
                <tr key={doc.id} className="hover:bg-white/[0.03]">
                  <td className="px-5 py-3.5 font-medium text-[var(--cl-text)]">{doc.name}</td>
                  <td className="px-4 py-3.5 text-xs text-[var(--cl-muted)]">{doc.fileType}</td>
                  <td className="px-4 py-3.5 text-xs text-[var(--cl-muted)]">{doc.dateAnalyzed}</td>
                  <td className="px-4 py-3.5 text-xs font-semibold">{doc.clausesFound}</td>
                  <td className="px-4 py-3.5">
                    <RiskBadge level={`${doc.riskScore}/100 · ${doc.riskLevel}`} />
                  </td>
                  <td className="px-4 py-3.5 text-xs font-semibold text-emerald-400">
                    {doc.status}
                  </td>
                  <td className="px-5 py-3.5 text-right">
                    <div className="inline-flex items-center gap-2">
                      <button
                        onClick={() => navigate(`/analysis/${doc.id}`)}
                        className="rounded-lg bg-[#9B7AFF]/15 px-3 py-1 text-xs font-semibold text-[#B79EFF] hover:bg-[#9B7AFF] hover:text-white"
                      >
                        View
                      </button>
                      <button
                        onClick={() => reanalyzeDocument(doc.id)}
                        className="rounded-lg p-1.5 text-[var(--cl-muted)] hover:bg-white/10"
                        title="Re-analyze"
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => deleteDocument(doc.id)}
                        className="rounded-lg p-1.5 text-red-400 hover:bg-red-500/15"
                        title="Delete"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
