import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getOrganizationDisputeSettings,
  updateOrganizationDisputeSettings,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useState } from 'react';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function DisputeSettingsCard() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ['org-admin-dispute-settings'],
    queryFn: getOrganizationDisputeSettings,
  });
  const [tolerance, setTolerance] = useState('');
  const [baselineDays, setBaselineDays] = useState('');
  const [recentDays, setRecentDays] = useState('');

  const save = useMutation({
    mutationFn: updateOrganizationDisputeSettings,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['org-admin-dispute-settings'] });
      void queryClient.invalidateQueries({ queryKey: ['reporting-reinvestigation-benchmarks'] });
    },
  });

  if (isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading dispute settings…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-red-600">Failed to load dispute settings.</p>
      </Card>
    );
  }

  const currentTolerance = tolerance || data.cross_bureau_balance_tolerance;
  const currentBaseline = baselineDays || String(data.reinvestigation_benchmark_baseline_days);
  const currentRecent = recentDays || String(data.reinvestigation_benchmark_recent_days);

  return (
    <Card className="mb-6" title="Dispute settings">
      <p className="text-sm text-gray-600">
        Cross-bureau monetary tolerance and default windows for org-internal reinvestigation outcome
        benchmarks.
      </p>
      <label
        className="mt-4 block text-sm font-medium text-gray-700"
        htmlFor="cross-bureau-tolerance"
      >
        Cross-bureau balance tolerance (USD)
      </label>
      <input
        id="cross-bureau-tolerance"
        className={inputClass}
        type="number"
        min="0.01"
        max="100"
        step="0.01"
        value={currentTolerance}
        onChange={(event) => setTolerance(event.target.value)}
      />
      <p className="mt-2 text-xs text-gray-500">
        Platform default: ${data.platform_default_tolerance}
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium text-gray-700" htmlFor="benchmark-baseline">
          Benchmark baseline window (days)
          <input
            id="benchmark-baseline"
            className={inputClass}
            type="number"
            min={7}
            max={365}
            value={currentBaseline}
            onChange={(event) => setBaselineDays(event.target.value)}
          />
        </label>
        <label className="block text-sm font-medium text-gray-700" htmlFor="benchmark-recent">
          Benchmark recent window (days)
          <input
            id="benchmark-recent"
            className={inputClass}
            type="number"
            min={1}
            max={365}
            value={currentRecent}
            onChange={(event) => setRecentDays(event.target.value)}
          />
        </label>
      </div>
      <p className="mt-2 text-xs text-gray-500">
        Platform defaults: {data.platform_default_baseline_days}d /{' '}
        {data.platform_default_recent_days}d. Recent must be ≤ baseline. Last updated:{' '}
        {data.updated_at ? new Date(data.updated_at).toLocaleString() : 'never (using defaults)'}
      </p>
      <Button
        className="mt-4"
        disabled={save.isPending}
        onClick={() =>
          save.mutate({
            cross_bureau_balance_tolerance: currentTolerance,
            reinvestigation_benchmark_baseline_days: Number.parseInt(currentBaseline, 10),
            reinvestigation_benchmark_recent_days: Number.parseInt(currentRecent, 10),
          })
        }
      >
        {save.isPending ? 'Saving…' : 'Save dispute settings'}
      </Button>
      {save.isError ? (
        <p className="mt-2 text-sm text-red-600">Failed to save dispute settings.</p>
      ) : null}
    </Card>
  );
}
