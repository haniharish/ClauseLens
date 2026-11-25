export function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function getRiskStyles(level) {
  const normalized = (level || '').toLowerCase();
  if (normalized.includes('high') || normalized === 'critical') {
    return {
      badge: 'bg-red-500/15 text-red-400 border border-red-500/30',
      dot: 'bg-red-400',
      bar: 'bg-gradient-to-r from-red-500 to-rose-400',
      text: 'text-red-400',
    };
  }
  if (normalized.includes('medium') || normalized === 'moderate' || normalized === 'warning') {
    return {
      badge: 'bg-amber-500/15 text-amber-400 border border-amber-500/30',
      dot: 'bg-amber-400',
      bar: 'bg-gradient-to-r from-amber-500 to-orange-400',
      text: 'text-amber-400',
    };
  }
  return {
    badge: 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30',
    dot: 'bg-emerald-400',
    bar: 'bg-gradient-to-r from-emerald-500 to-teal-400',
    text: 'text-emerald-400',
  };
}

export function getScoreLabel(score) {
  if (score >= 75) return 'High Risk';
  if (score >= 45) return 'Moderate';
  return 'Low Risk';
}

export function computePersonalizedScore(baseScore, category, profile) {
  if (!profile) return baseScore;
  let boost = 0;
  const uses = profile.intendedUse || [];
  if (uses.includes('Student') && ['Data Sharing', 'Data Collection', 'Account Termination'].includes(category)) {
    boost += 5;
  }
  if (uses.includes('Freelancer') && ['Auto-Renewal & Fees', 'Arbitration', 'Account Termination'].includes(category)) {
    boost += 6;
  }
  if (uses.includes('Business Owner') && ['Arbitration', 'Data Sharing', 'Auto-Renewal & Fees'].includes(category)) {
    boost += 7;
  }
  if (uses.includes('Parent of Minor') && ['Data Collection', 'Data Sharing'].includes(category)) {
    boost += 9;
  }
  if (profile.jurisdiction === 'European Union' && category === 'Data Sharing') {
    boost += 4;
  }
  return Math.min(99, Math.max(12, baseScore + boost));
}
