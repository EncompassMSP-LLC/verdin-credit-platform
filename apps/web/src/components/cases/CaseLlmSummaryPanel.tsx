import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { generateCaseLlmSummary, getLlmStatus, type CaseLlmSummary } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { featureFlags } from '../../lib/feature-flags';

function formatGeneratedAt(value: string) {
  return new Date(value).toLocaleString();
}

interface CaseLlmSummaryPanelProps {
  caseId: string;
}

export function CaseLlmSummaryPanel({ caseId }: CaseLlmSummaryPanelProps) {
  const [summary, setSummary] = useState<CaseLlmSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['llm-status'],
    queryFn: getLlmStatus,
    enabled: featureFlags.enableLlm,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateCaseLlmSummary(caseId),
    onSuccess: (result) => {
      setSummary(result);
      setError(null);
    },
    onError: (err: Error) => setError(err.message),
  });

  if (!featureFlags.enableLlm) {
    return null;
  }

  const ready = statusQuery.data?.ready ?? false;
  const blockers = statusQuery.data?.blockers ?? [];

  return (
    <Card title="AI case summary" className="lg:col-span-3">
      <p className="text-sm text-gray-600">
        Generate a PII-scrubbed case summary using the configured LLM provider.
      </p>

      {statusQuery.isLoading ? (
        <p className="mt-4 text-sm text-gray-500">Checking LLM readiness…</p>
      ) : null}

      {statusQuery.isError ? (
        <p className="mt-4 text-sm text-red-600">Failed to load LLM status.</p>
      ) : null}

      {statusQuery.data && !ready ? (
        <div className="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-900">
          <p className="font-medium">LLM summary is not ready.</p>
          {blockers.length > 0 ? (
            <ul className="mt-2 list-disc pl-5">
              {blockers.map((blocker) => (
                <li key={blocker}>{blocker.replaceAll('_', ' ')}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      <div className="mt-4">
        <Button
          type="button"
          onClick={() => {
            setError(null);
            generateMutation.mutate();
          }}
          loading={generateMutation.isPending}
          disabled={!ready || generateMutation.isPending}
        >
          Generate summary
        </Button>
      </div>

      {error ? (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {summary ? (
        <div className="mt-6 space-y-3 border-t border-gray-200 pt-6">
          <p className="whitespace-pre-wrap text-sm text-gray-800">{summary.summary}</p>
          <dl className="grid grid-cols-1 gap-2 text-xs text-gray-500 sm:grid-cols-2">
            <div>
              <dt className="inline">Provider: </dt>
              <dd className="inline">{summary.provider}</dd>
            </div>
            <div>
              <dt className="inline">Model: </dt>
              <dd className="inline">{summary.model}</dd>
            </div>
            <div>
              <dt className="inline">Generated: </dt>
              <dd className="inline">{formatGeneratedAt(summary.generated_at)}</dd>
            </div>
            <div>
              <dt className="inline">PII scrubbed: </dt>
              <dd className="inline">{summary.pii_scrubbed ? 'Yes' : 'No'}</dd>
            </div>
          </dl>
        </div>
      ) : null}
    </Card>
  );
}
