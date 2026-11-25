import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Eye, GitCompareArrows, Pause, Play, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';
import Modal from '../components/common/Modal';
import DemoBanner from '../components/common/DemoBanner';
import EmptyState from '../components/common/EmptyState';

export default function PolicyMonitoring() {
  const {
    monitoredPolicies,
    addMonitoredPolicy,
    togglePolicyMonitoring,
    removeMonitoredPolicy,
  } = useApp();
  const navigate = useNavigate();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form, setForm] = useState({ service: '', policyName: '', url: '' });

  const handleAddPolicy = async (e) => {
    e.preventDefault();
    if (!form.service.trim() || !form.policyName.trim() || !form.url.trim()) {
      toast.error('Please fill in service name, policy title, and URL');
      return;
    }
    try {
      new URL(form.url.trim());
    } catch {
      toast.error('Please enter a valid https:// policy URL');
      return;
    }
    await addMonitoredPolicy(form);
    setForm({ service: '', policyName: '', url: '' });
    setIsModalOpen(false);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
            Policy Monitoring
          </h1>
          <p className="mt-1 text-sm text-[var(--cl-muted)]">
            Track live policy URLs for silent updates and version diffs.
          </p>
        </div>

        <button onClick={() => setIsModalOpen(true)} className="cl-btn-primary">
          <Plus className="h-4 w-4" />
          Add Policy
        </button>
      </div>

      <DemoBanner message="Demonstration Data: Sample monitored policies (Google, Instagram, Amazon, Microsoft) simulate scheduled Celery web-crawler checks." />

      {monitoredPolicies.length === 0 ? (
        <EmptyState
          icon={Eye}
          title="No monitored policies yet"
          description="Add a website Terms & Conditions or Privacy Policy URL to receive personalized change alerts."
          action={
            <button onClick={() => setIsModalOpen(true)} className="cl-btn-primary">
              <Plus className="h-4 w-4" />
              Add Policy
            </button>
          }
        />
      ) : (
        <div className="glass-card overflow-hidden">
          <div className="flex items-center justify-between border-b border-[var(--cl-border)] px-6 py-4">
            <span className="text-sm font-semibold text-[var(--cl-text)]">
              Monitored Services ({monitoredPolicies.length})
            </span>
            <span className="rounded-full border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 px-2.5 py-0.5 text-[11px] font-medium text-[#B79EFF]">
              Demonstration Data
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-left text-sm">
              <thead>
                <tr className="border-b border-[var(--cl-border)] bg-[var(--cl-bg)]/50 text-xs font-semibold uppercase text-[var(--cl-muted)]">
                  <th className="px-6 py-3.5">Website / Service</th>
                  <th className="px-4 py-3.5">Policy Name</th>
                  <th className="px-4 py-3.5">Last Checked</th>
                  <th className="px-4 py-3.5">Current Version</th>
                  <th className="px-4 py-3.5">Monitoring Status</th>
                  <th className="px-4 py-3.5">Latest Change</th>
                  <th className="px-6 py-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--cl-border)]">
                {monitoredPolicies.map((pol) => (
                  <tr key={pol.id} className="hover:bg-white/[0.03]">
                    <td className="px-6 py-4">
                      <p className="font-semibold text-[var(--cl-text)]">{pol.service}</p>
                      <p className="max-w-[180px] truncate text-[11px] text-[var(--cl-muted)]">
                        {pol.url}
                      </p>
                    </td>
                    <td className="px-4 py-4 text-xs font-medium text-[var(--cl-text)]">
                      {pol.policyName}
                    </td>
                    <td className="px-4 py-4 text-xs text-[var(--cl-muted)]">{pol.lastChecked}</td>
                    <td className="px-4 py-4">
                      <span className="rounded-md border border-[var(--cl-border)] bg-[var(--cl-bg)] px-2 py-0.5 font-mono text-xs text-cyan-400">
                        {pol.currentVersion}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${
                          pol.status === 'Active'
                            ? 'border border-emerald-500/30 bg-emerald-500/15 text-emerald-400'
                            : 'border border-amber-500/30 bg-amber-500/15 text-amber-400'
                        }`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${
                            pol.status === 'Active' ? 'bg-emerald-400' : 'bg-amber-400'
                          }`}
                        />
                        {pol.status}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-xs text-[var(--cl-muted)]">{pol.latestChange}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="inline-flex items-center gap-1.5">
                        <button
                          onClick={() => {
                            togglePolicyMonitoring(pol.id);
                            toast.success(
                              pol.status === 'Active'
                                ? `Paused monitoring for ${pol.service}`
                                : `Resumed monitoring for ${pol.service}`
                            );
                          }}
                          className="rounded-lg border border-[var(--cl-border)] p-1.5 text-[var(--cl-muted)] transition hover:border-[#9B7AFF]/40 hover:text-[var(--cl-text)]"
                          title={pol.status === 'Active' ? 'Pause monitoring' : 'Start monitoring'}
                        >
                          {pol.status === 'Active' ? (
                            <Pause className="h-3.5 w-3.5" />
                          ) : (
                            <Play className="h-3.5 w-3.5" />
                          )}
                        </button>
                        <button
                          onClick={() => navigate('/version-history')}
                          className="inline-flex items-center gap-1 rounded-lg border border-[#9B7AFF]/35 bg-[#9B7AFF]/10 px-2.5 py-1.5 text-xs font-semibold text-[#B79EFF] hover:bg-[#9B7AFF] hover:text-white"
                        >
                          <GitCompareArrows className="h-3.5 w-3.5" />
                          History
                        </button>
                        <button
                          onClick={() => removeMonitoredPolicy(pol.id)}
                          className="rounded-lg p-1.5 text-red-400 hover:bg-red-500/15"
                          title="Remove policy"
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
        </div>
      )}

      {/* Add Monitored Policy Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Policy to Monitor"
        subtitle="Enter a Terms & Conditions or Privacy Policy URL to track future updates (Demo)."
      >
        <form onSubmit={handleAddPolicy} className="space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-text)]">
              Website / Service Name
            </label>
            <input
              type="text"
              value={form.service}
              onChange={(e) => setForm({ ...form, service: e.target.value })}
              placeholder="e.g., Spotify"
              className="cl-input"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-text)]">
              Policy Name
            </label>
            <input
              type="text"
              value={form.policyName}
              onChange={(e) => setForm({ ...form, policyName: e.target.value })}
              placeholder="e.g., Spotify Privacy Policy"
              className="cl-input"
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-text)]">
              Policy URL
            </label>
            <input
              type="url"
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              placeholder="https://www.spotify.com/legal/privacy-policy/"
              className="cl-input"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsModalOpen(false)}
              className="cl-btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="cl-btn-primary">
              Start Monitoring
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
