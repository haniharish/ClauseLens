import { useState } from 'react';
import { Check, Edit3, Globe2, Lock, Save, ShieldCheck, User } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';

const AGE_GROUPS = ['Under 13', '13–17', '18–64', '65+'];
const INTENDED_USES = [
  'Personal',
  'Student',
  'Freelancer',
  'Business Owner',
  'Parent of Minor',
];
const JURISDICTIONS = ['India', 'European Union', 'United States', 'Other'];

export default function Profile() {
  const { profile, updateProfile } = useApp();
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState(profile);

  const toggleUse = (useCase) => {
    if (!isEditing) return;
    setForm((prev) => {
      const exists = prev.intendedUse.includes(useCase);
      const next = exists
        ? prev.intendedUse.filter((u) => u !== useCase)
        : [...prev.intendedUse, useCase];
      return { ...prev, intendedUse: next.length ? next : ['Personal'] };
    });
  };

  const handleSave = (e) => {
    e.preventDefault();
    if (!form.fullName.trim() || !form.email.trim()) {
      toast.error('Name and email are required');
      return;
    }
    updateProfile(form);
    setIsEditing(false);
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Your Personal Profile
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Customize your context dimensions so ClauseLens highlights the clauses that matter most to you.
          </p>
        </div>

        {!isEditing ? (
          <button onClick={() => setIsEditing(true)} className="cl-btn-primary">
            <Edit3 className="h-4 w-4" />
            Edit Profile
          </button>
        ) : (
          <button
            onClick={() => {
              setForm(profile);
              setIsEditing(false);
            }}
            className="cl-btn-secondary"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Why We Ask Explanation */}
      <div className="glass-card border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 p-4 flex items-start gap-3">
        <ShieldCheck className="h-5 w-5 shrink-0 text-[#9B7AFF] mt-0.5" />
        <p className="text-xs leading-relaxed text-[var(--cl-text)]">
          ClauseLens uses three lightweight context dimensions — <strong>Age Group</strong>,{' '}
          <strong>Intended Use</strong>, and <strong>Jurisdiction</strong> — to compute personalized
          relevance scores via Sentence Transformers. We intentionally avoid collecting unnecessary
          sensitive personal data.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Dimension 1: Personal Information */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[var(--cl-border)] pb-3">
            <User className="h-4 w-4 text-[#9B7AFF]" />
            <h2 className="text-base font-semibold text-[var(--cl-text)]">Personal Information</h2>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-muted)]">
                Full Name
              </label>
              <input
                type="text"
                disabled={!isEditing}
                value={form.fullName}
                onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                className="cl-input disabled:opacity-70"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-muted)]">
                Email Address
              </label>
              <input
                type="email"
                disabled={!isEditing}
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                className="cl-input disabled:opacity-70"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-xs font-semibold text-[var(--cl-muted)]">
              Age Group
            </label>
            <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
              {AGE_GROUPS.map((group) => {
                const active = form.ageGroup === group;
                return (
                  <button
                    key={group}
                    type="button"
                    disabled={!isEditing}
                    onClick={() => setForm({ ...form, ageGroup: group })}
                    className={`rounded-xl border px-3 py-2.5 text-xs font-semibold transition ${
                      active
                        ? 'border-[#9B7AFF] bg-[#9B7AFF]/20 text-[var(--cl-text)]'
                        : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-[var(--cl-muted)]'
                    } ${!isEditing ? 'cursor-default opacity-85' : 'hover:border-[#9B7AFF]/50'}`}
                  >
                    {group}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Dimension 2: Intended Use */}
        <div className="glass-card p-6 space-y-4">
          <div>
            <h2 className="text-base font-semibold text-[var(--cl-text)]">Intended Use</h2>
            <p className="text-xs text-[var(--cl-muted)]">
              Select one or more roles that describe how you use online services
            </p>
          </div>

          <div className="flex flex-wrap gap-2.5">
            {INTENDED_USES.map((role) => {
              const selected = form.intendedUse.includes(role);
              return (
                <button
                  key={role}
                  type="button"
                  disabled={!isEditing}
                  onClick={() => toggleUse(role)}
                  className={`inline-flex items-center gap-2 rounded-xl border px-4 py-2.5 text-xs font-semibold transition ${
                    selected
                      ? 'border-[#9B7AFF] bg-[#9B7AFF]/20 text-[var(--cl-text)]'
                      : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-[var(--cl-muted)]'
                  } ${!isEditing ? 'cursor-default opacity-85' : 'hover:border-[#9B7AFF]/50'}`}
                >
                  {selected && <Check className="h-3.5 w-3.5 text-[#9B7AFF]" />}
                  {role}
                </button>
              );
            })}
          </div>
        </div>

        {/* Dimension 3: Jurisdiction & Local Privacy */}
        <div className="glass-card p-6 space-y-4">
          <div className="flex items-center gap-2 border-b border-[var(--cl-border)] pb-3">
            <Globe2 className="h-4 w-4 text-cyan-400" />
            <h2 className="text-base font-semibold text-[var(--cl-text)]">
              Jurisdiction &amp; Privacy
            </h2>
          </div>

          <div className="max-w-sm">
            <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-muted)]">
              Primary Legal Jurisdiction
            </label>
            <select
              disabled={!isEditing}
              value={form.jurisdiction}
              onChange={(e) => setForm({ ...form, jurisdiction: e.target.value })}
              className="cl-input cursor-pointer disabled:opacity-70"
            >
              {JURISDICTIONS.map((j) => (
                <option key={j} value={j}>
                  {j}
                </option>
              ))}
            </select>
          </div>

          <label className="flex items-center justify-between gap-4 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/55 p-4 cursor-pointer">
            <div className="flex items-start gap-3">
              <Lock className="mt-0.5 h-4 w-4 text-[#9B7AFF]" />
              <div>
                <p className="text-xs font-semibold text-[var(--cl-text)]">
                  Keep my profile on this device where supported.
                </p>
                <p className="mt-0.5 text-[11px] text-[var(--cl-muted)]">
                  Stores your personalization preferences locally in browser storage instead of syncing externally.
                </p>
              </div>
            </div>
            <input
              type="checkbox"
              disabled={!isEditing}
              checked={form.keepLocalOnly}
              onChange={(e) => setForm({ ...form, keepLocalOnly: e.target.checked })}
              className="h-4 w-4 accent-[#9B7AFF]"
            />
          </label>
        </div>

        {isEditing && (
          <div className="flex justify-end">
            <button type="submit" className="cl-btn-primary px-6">
              <Save className="h-4 w-4" />
              Save Profile
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
