import { useNavigate } from 'react-router-dom';
import { AlertTriangle, CheckCircle2, Globe2, Sparkles, UserCheck } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export default function PersonalInsightsCard() {
  const { profile } = useApp();
  const navigate = useNavigate();

  const primaryUse = profile.intendedUse?.includes('Student')
    ? 'Student'
    : profile.intendedUse?.[0] || 'Personal';

  return (
    <div className="space-y-4">
      {/* Purple Gradient Portfolio-Inspired Feature Card */}
      <div className="purple-feature-card relative overflow-hidden p-6 text-white">
        <div className="pointer-events-none absolute -right-10 -top-10 h-36 w-36 rounded-full bg-white/15 blur-2xl" />
        <div className="pointer-events-none absolute -bottom-12 -left-10 h-36 w-36 rounded-full bg-cyan-400/20 blur-2xl" />

        <div className="relative">
          <div className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-1 text-[11px] font-semibold backdrop-blur-sm">
            <Sparkles className="h-3.5 w-3.5" />
            Context-Aware AI Engine
          </div>

          <h2 className="text-lg font-bold tracking-tight">Your Personal Legal Insights</h2>
          <p className="mt-1.5 text-xs leading-relaxed text-white/85">
            ClauseLens analyzes policies according to your age, intended use and jurisdiction.
          </p>

          <div className="mt-5 space-y-2.5 rounded-xl bg-black/20 p-3.5 backdrop-blur-sm border border-white/15">
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-2 text-white/80">
                <UserCheck className="h-3.5 w-3.5" />
                User type
              </span>
              <span className="font-semibold text-white">{primaryUse}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-2 text-white/80">
                <Globe2 className="h-3.5 w-3.5" />
                Jurisdiction
              </span>
              <span className="font-semibold text-white">{profile.jurisdiction}</span>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-2 text-white/80">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Profile status
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-400/20 px-2 py-0.5 text-[11px] font-semibold text-emerald-200">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-300" />
                {profile.profileStatus || 'Active'}
              </span>
            </div>
          </div>

          <button
            onClick={() => navigate('/profile')}
            className="mt-4 w-full rounded-xl bg-white px-4 py-2.5 text-xs font-bold text-[#5B36E0] shadow-lg transition hover:bg-slate-100 active:scale-[0.98]"
          >
            Update My Profile
          </button>
        </div>
      </div>

      {/* Attention Alert Small Card */}
      <div
        onClick={() => navigate('/analysis/doc-google-privacy')}
        className="glass-card glass-card-hover cursor-pointer p-4 border-l-4 border-l-amber-400"
      >
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-500/15 text-amber-400">
            <AlertTriangle className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold text-[var(--cl-text)]">
              3 clauses require your attention.
            </p>
            <p className="mt-0.5 text-xs text-[var(--cl-muted)]">
              High relevance to your {primaryUse} ({profile.jurisdiction}) profile. Click to review.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
