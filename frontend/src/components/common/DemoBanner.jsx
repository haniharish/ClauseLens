import { Info } from 'lucide-react';
import { USE_MOCK_API } from '../../services/api';

export default function DemoBanner({ message }) {
  if (!USE_MOCK_API) return null;
  return (
    <div className="flex items-center gap-2.5 rounded-xl border border-[#9B7AFF]/25 bg-[#9B7AFF]/10 px-3.5 py-2 text-xs text-[var(--cl-muted)]">
      <Info className="h-4 w-4 shrink-0 text-[#9B7AFF]" />
      <span>
        <strong className="font-semibold text-[var(--cl-text)]">Frontend Preview Mode:</strong>{' '}
        {message ||
          'Displaying simulated sample data for demonstration. Live NLP summarization and policy crawling connect via the Django REST API.'}
      </span>
    </div>
  );
}
