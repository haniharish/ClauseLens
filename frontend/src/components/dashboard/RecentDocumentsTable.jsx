import { useNavigate } from 'react-router-dom';
import { ArrowRight, FileText } from 'lucide-react';
import { RiskBadge } from '../common/Badge';

export default function RecentDocumentsTable({ documents = [] }) {
  const navigate = useNavigate();

  return (
    <div className="glass-card glass-card-hover overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--cl-border)] px-6 py-5">
        <div>
          <h2 className="text-lg font-semibold text-[var(--cl-text)]">
            Recently Analyzed Documents
          </h2>
          <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
            Click any policy to inspect AI clause summaries and legal risk highlights
          </p>
        </div>
        <button
          onClick={() => navigate('/documents')}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#9B7AFF] hover:underline"
        >
          View all documents
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-left text-sm">
          <thead>
            <tr className="border-b border-[var(--cl-border)] bg-[var(--cl-bg)]/45 text-xs font-semibold uppercase tracking-wider text-[var(--cl-muted)]">
              <th className="px-6 py-3.5">Document Name</th>
              <th className="px-4 py-3.5">Document Type</th>
              <th className="px-4 py-3.5">Date Analyzed</th>
              <th className="px-4 py-3.5">Clauses Found</th>
              <th className="px-4 py-3.5">Risk Level</th>
              <th className="px-6 py-3.5 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--cl-border)]">
            {documents.map((doc) => (
              <tr
                key={doc.id}
                className="transition-colors hover:bg-white/[0.03]"
              >
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#9B7AFF]/15 text-[#9B7AFF]">
                      <FileText className="h-4 w-4" />
                    </div>
                    <span className="font-medium text-[var(--cl-text)]">{doc.name}</span>
                  </div>
                </td>
                <td className="px-4 py-4 text-xs text-[var(--cl-muted)]">{doc.type}</td>
                <td className="px-4 py-4 text-xs text-[var(--cl-muted)]">{doc.dateAnalyzed}</td>
                <td className="px-4 py-4 text-xs font-semibold text-[var(--cl-text)]">
                  {doc.clausesFound}
                </td>
                <td className="px-4 py-4">
                  <RiskBadge level={doc.riskLevel} />
                </td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => navigate(`/analysis/${doc.id}`)}
                    className="rounded-xl border border-[#9B7AFF]/35 bg-[#9B7AFF]/10 px-3 py-1.5 text-xs font-semibold text-[#B79EFF] transition hover:bg-[#9B7AFF] hover:text-white"
                  >
                    View Analysis
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
