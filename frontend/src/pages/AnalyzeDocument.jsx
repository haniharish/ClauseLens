import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import {
  CheckCircle2,
  FileText,
  Globe,
  Loader2,
  Sparkles,
  Trash2,
  UploadCloud,
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';
import { documentService } from '../services/documentService';
import { formatFileSize } from '../utils/helpers';
import DemoBanner from '../components/common/DemoBanner';

const ANALYSIS_STEPS = [
  'Extracting document text',
  'Identifying clauses',
  'Classifying risk categories',
  'Generating AI summaries',
  'Calculating personalized relevance',
  'Preparing final report',
];

export default function AnalyzeDocument() {
  const { addAnalyzedDocument, profile } = useApp();
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [policyUrl, setPolicyUrl] = useState('');
  const [docType, setDocType] = useState('Terms & Conditions');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      toast.error('Please upload a valid PDF file under 15 MB');
      return;
    }
    const selected = acceptedFiles[0];
    if (selected) {
      setFile(selected);
      setUploadProgress(0);
      toast.success(`Selected ${selected.name}`);
    }
  }, []);

  // Simulate crisp upload progress bar when a file is attached
  useEffect(() => {
    if (!file) return;
    setUploadProgress(15);
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 25;
      });
    }, 120);
    return () => clearInterval(interval);
  }, [file]);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxSize: 15 * 1024 * 1024,
    multiple: false,
    noClick: true,
  });

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!file && !policyUrl.trim()) {
      toast.error('Please upload a PDF file or enter a policy URL');
      return;
    }

    if (policyUrl.trim() && !file) {
      try {
        new URL(policyUrl.trim());
      } catch {
        toast.error('Please enter a valid URL starting with https:// or http://');
        return;
      }
    }

    setIsAnalyzing(true);
    setCurrentStep(0);

    for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
      setCurrentStep(i);
      // eslint-disable-next-line no-await-in-loop
      await new Promise((resolve) => setTimeout(resolve, 650));
    }

    try {
      const created = await documentService.uploadAndAnalyze({
        file,
        policyUrl: policyUrl.trim(),
        docType,
      });
      addAnalyzedDocument(created);
      toast.success('Document analysis completed');
      navigate(`/analysis/${created.id}`);
    } catch {
      toast.error('Analysis failed');
      setIsAnalyzing(false);
    }
  };

  if (isAnalyzing) {
    const percent = Math.round(((currentStep + 1) / ANALYSIS_STEPS.length) * 100);
    return (
      <div className="mx-auto max-w-2xl py-8">
        <div className="glass-card p-8">
          <div className="flex flex-col items-center text-center">
            <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#9B7AFF]/15 text-[#9B7AFF] border border-[#9B7AFF]/30 shadow-glow-purple">
              <Sparkles className="h-8 w-8 animate-pulse" />
            </div>
            <h2 className="text-xl font-bold text-[var(--cl-text)]">
              Analyzing Policy Document...
            </h2>
            <p className="mt-1 text-xs text-[var(--cl-muted)]">
              Personalizing risk relevance for {profile.intendedUse?.join(', ')} ({profile.jurisdiction})
            </p>
          </div>

          <div className="mt-6">
            <div className="mb-2 flex items-center justify-between text-xs">
              <span className="font-medium text-[#9B7AFF]">Pipeline Progress</span>
              <span className="font-bold text-[var(--cl-text)]">{percent}%</span>
            </div>
            <div className="h-2.5 w-full overflow-hidden rounded-full bg-[var(--cl-bg)]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[#9B7AFF] via-[#3B82F6] to-[#06B6D4] transition-all duration-500"
                style={{ width: `${percent}%` }}
              />
            </div>
          </div>

          <div className="mt-6 space-y-3">
            {ANALYSIS_STEPS.map((step, idx) => {
              const done = idx < currentStep;
              const active = idx === currentStep;
              return (
                <div
                  key={step}
                  className={`flex items-center justify-between rounded-xl border px-4 py-3 text-sm transition-all ${
                    active
                      ? 'border-[#9B7AFF]/50 bg-[#9B7AFF]/10 text-[var(--cl-text)]'
                      : done
                      ? 'border-emerald-500/25 bg-emerald-500/5 text-emerald-400'
                      : 'border-[var(--cl-border)] bg-[var(--cl-bg)]/40 text-[var(--cl-muted)]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    {done ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                    ) : active ? (
                      <Loader2 className="h-4 w-4 animate-spin text-[#9B7AFF]" />
                    ) : (
                      <span className="h-2 w-2 rounded-full bg-slate-600 ml-1 mr-1" />
                    )}
                    <span className="font-medium">{step}</span>
                  </div>
                  <span className="text-[11px] font-semibold">
                    {done ? 'Done' : active ? 'Processing...' : 'Queued'}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-[var(--cl-text)]">
          Analyze a Document
        </h1>
        <p className="mt-1 text-sm text-[var(--cl-muted)]">
          Understand complex Terms &amp; Conditions in simple language.
        </p>
      </div>

      <DemoBanner message="Uploads and URL submissions simulate the NLP pipeline locally with mock results until connected to your Django + Hugging Face backend." />

      <form onSubmit={handleAnalyze} className="space-y-6">
        {/* Document Upload Dropzone */}
        <div className="glass-card p-6">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-semibold text-[var(--cl-text)]">
                Upload Legal Document (PDF)
              </h2>
              <p className="text-xs text-[var(--cl-muted)]">
                Supported file type: PDF only · Maximum file size: 15 MB
              </p>
            </div>
            <span className="rounded-lg border border-[#9B7AFF]/30 bg-[#9B7AFF]/10 px-2.5 py-1 text-[11px] font-semibold text-[#9B7AFF]">
              PDF up to 15 MB
            </span>
          </div>

          <div
            {...getRootProps()}
            className={`flex flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition-all ${
              isDragActive
                ? 'border-[#9B7AFF] bg-[#9B7AFF]/10'
                : 'border-[var(--cl-border-light)] bg-[var(--cl-bg)]/50 hover:border-[#9B7AFF]/50'
            }`}
          >
            <input {...getInputProps()} />
            <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[#9B7AFF]/15 text-[#9B7AFF]">
              <UploadCloud className="h-7 w-7" />
            </div>
            <p className="text-sm font-semibold text-[var(--cl-text)]">
              {isDragActive
                ? 'Drop your PDF policy here...'
                : 'Drag and drop your PDF document here'}
            </p>
            <p className="mt-1 text-xs text-[var(--cl-muted)]">
              Supports Terms of Service, Privacy Policies, EULAs, and SaaS Agreements
            </p>
            <button
              type="button"
              onClick={open}
              className="cl-btn-secondary mt-5 text-xs"
            >
              Browse Files
            </button>
          </div>

          {/* Attached File Preview */}
          {file && (
            <div className="mt-4 rounded-xl border border-[var(--cl-border)] bg-[var(--cl-bg)]/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-red-500/15 text-red-400">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-[var(--cl-text)]">
                      {file.name}
                    </p>
                    <p className="text-xs text-[var(--cl-muted)]">
                      {formatFileSize(file.size)} · PDF Document
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFile(null);
                    setUploadProgress(0);
                  }}
                  className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/10"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Remove
                </button>
              </div>
              <div className="mt-3">
                <div className="mb-1 flex justify-between text-[11px] text-[var(--cl-muted)]">
                  <span>File Upload Progress</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/5">
                  <div
                    className="h-full rounded-full bg-emerald-400 transition-all duration-200"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>

        {/* OR Enter Policy URL + Document Type */}
        <div className="glass-card p-6 space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="sm:col-span-2">
              <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-text)]">
                Enter Policy URL (Optional)
              </label>
              <div className="relative">
                <Globe className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--cl-muted)]" />
                <input
                  type="url"
                  value={policyUrl}
                  onChange={(e) => setPolicyUrl(e.target.value)}
                  placeholder="https://example.com/privacy-policy"
                  className="cl-input pl-10"
                />
              </div>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold text-[var(--cl-text)]">
                Document Type
              </label>
              <select
                value={docType}
                onChange={(e) => setDocType(e.target.value)}
                className="cl-input cursor-pointer"
              >
                <option value="Terms & Conditions">Terms &amp; Conditions</option>
                <option value="Privacy Policy">Privacy Policy</option>
                <option value="User Agreement">User Agreement</option>
                <option value="Services Agreement">Services Agreement</option>
              </select>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-4 border-t border-[var(--cl-border)] pt-4">
            <p className="text-xs text-[var(--cl-muted)]">
              Active personalization:{' '}
              <span className="font-semibold text-[var(--cl-text)]">
                {profile.intendedUse?.join(', ')} · {profile.jurisdiction}
              </span>
            </p>
            <button type="submit" className="cl-btn-primary px-6 py-3">
              <Sparkles className="h-4 w-4" />
              Analyze Document
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}
