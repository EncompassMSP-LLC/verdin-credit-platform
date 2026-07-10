import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  generateAccountLlmRecommendation,
  getLlmStatus,
  type AccountLlmRecommendation,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { featureFlags } from '../../lib/feature-flags';

function formatGeneratedAt(value: string) {
  return new Date(value).toLocaleString();
}

interface AccountLlmRecommendationPanelProps {
  accountId: string;
}

export function AccountLlmRecommendationPanel({ accountId }: AccountLlmRecommendationPanelProps) {
  const queryClient = useQueryClient();
  const [recommendation, setRecommendation] = useState<AccountLlmRecommendation | null>(null);
  const [error, setError] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['llm-status'],
    queryFn: getLlmStatus,
    enabled: featureFlags.enableLlm,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateAccountLlmRecommendation(accountId),
    onSuccess: (result) => {
      setRecommendation(result);
      setError(null);
      queryClient.invalidateQueries({ queryKey: ['account', accountId] });
      queryClient.invalidateQueries({ queryKey: ['accounts-intelligence'] });
    },
    onError: (err: Error) => setError(err.message),
  });

  if (!featureFlags.enableLlm) {
    return null;
  }

  const ready = statusQuery.data?.ready ?? false;
  const blockers = statusQuery.data?.blockers ?? [];

  return (
    <Card title="AI recommendation">
      <p className="text-sm text-gray-600">
        Generate a PII-scrubbed next-action recommendation using cross-bureau context when
        available.
      </p>

      {statusQuery.data && !ready ? (
        <div className="mt-4 rounded-md bg-amber-50 p-3 text-sm text-amber-900">
          <p className="font-medium">LLM recommendations are not ready.</p>
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
          Generate recommendation
        </Button>
      </div>

      {error ? (
        <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
      ) : null}

      {recommendation ? (
        <div className="mt-6 space-y-3 border-t border-gray-200 pt-6">
          <p className="text-sm text-gray-800">{recommendation.recommendation}</p>
          <dl className="grid grid-cols-1 gap-2 text-xs text-gray-500 sm:grid-cols-2">
            <div>
              <dt className="inline">Provider: </dt>
              <dd className="inline">{recommendation.provider}</dd>
            </div>
            <div>
              <dt className="inline">Model: </dt>
              <dd className="inline">{recommendation.model}</dd>
            </div>
            <div>
              <dt className="inline">Generated: </dt>
              <dd className="inline">{formatGeneratedAt(recommendation.generated_at)}</dd>
            </div>
            <div>
              <dt className="inline">Cross-bureau informed: </dt>
              <dd className="inline">{recommendation.cross_bureau_informed ? 'Yes' : 'No'}</dd>
            </div>
          </dl>
        </div>
      ) : null}
    </Card>
  );
}
