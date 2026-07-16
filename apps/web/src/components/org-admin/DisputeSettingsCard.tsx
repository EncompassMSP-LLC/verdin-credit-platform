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

  const save = useMutation({
    mutationFn: updateOrganizationDisputeSettings,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['org-admin-dispute-settings'] });
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

  const current = tolerance || data.cross_bureau_balance_tolerance;

  return (
    <Card className="mb-6" title="Dispute settings">
      <p className="text-sm text-gray-600">
        Cross-bureau monetary tolerance for litigation-packet discrepancy detection. Differences at
        or below this amount are treated as rounding noise.
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
        value={current}
        onChange={(event) => setTolerance(event.target.value)}
      />
      <p className="mt-2 text-xs text-gray-500">
        Platform default: ${data.platform_default_tolerance}. Last updated:{' '}
        {data.updated_at ? new Date(data.updated_at).toLocaleString() : 'never (using default)'}
      </p>
      <Button
        className="mt-4"
        disabled={save.isPending}
        onClick={() => save.mutate({ cross_bureau_balance_tolerance: current })}
      >
        {save.isPending ? 'Saving…' : 'Save tolerance'}
      </Button>
      {save.isError ? (
        <p className="mt-2 text-sm text-red-600">Failed to save dispute settings.</p>
      ) : null}
    </Card>
  );
}
