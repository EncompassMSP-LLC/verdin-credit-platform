import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getOrganizationDisputeSettings,
  updateOrganizationDisputeSettings,
  type BureauBenchmarkWindow,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useState } from 'react';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const BUREAU_WINDOW_OPTIONS = [
  { value: 'equifax', label: 'Equifax' },
  { value: 'experian', label: 'Experian' },
  { value: 'transunion', label: 'TransUnion' },
] as const;

type BureauKey = (typeof BUREAU_WINDOW_OPTIONS)[number]['value'];

type BureauDraft = Record<BureauKey, { baseline: string; recent: string }>;

function emptyBureauDraft(): BureauDraft {
  return {
    equifax: { baseline: '', recent: '' },
    experian: { baseline: '', recent: '' },
    transunion: { baseline: '', recent: '' },
  };
}

function draftFromSettings(
  windows: Record<string, BureauBenchmarkWindow> | undefined,
): BureauDraft {
  const draft = emptyBureauDraft();
  for (const bureau of BUREAU_WINDOW_OPTIONS) {
    const override = windows?.[bureau.value];
    if (override) {
      draft[bureau.value] = {
        baseline: String(override.baseline_days),
        recent: String(override.recent_days),
      };
    }
  }
  return draft;
}

export function DisputeSettingsCard() {
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ['org-admin-dispute-settings'],
    queryFn: getOrganizationDisputeSettings,
  });
  const [tolerance, setTolerance] = useState('');
  const [baselineDays, setBaselineDays] = useState('');
  const [recentDays, setRecentDays] = useState('');
  const [bureauDraft, setBureauDraft] = useState<BureauDraft | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const save = useMutation({
    mutationFn: updateOrganizationDisputeSettings,
    onSuccess: () => {
      setFormError(null);
      setBureauDraft(null);
      void queryClient.invalidateQueries({ queryKey: ['org-admin-dispute-settings'] });
      void queryClient.invalidateQueries({ queryKey: ['reporting-reinvestigation-benchmarks'] });
    },
    onError: (error: unknown) => {
      setFormError(error instanceof Error ? error.message : 'Failed to save dispute settings.');
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
  const currentBureauDraft =
    bureauDraft ?? draftFromSettings(data.reinvestigation_benchmark_bureau_windows);

  return (
    <Card className="mb-6" title="Dispute settings">
      <p className="text-sm text-gray-600">
        Cross-bureau monetary tolerance and default windows for org-internal reinvestigation outcome
        benchmarks. Optional per-bureau overrides apply when Reporting filters by that bureau.
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
          Org benchmark baseline window (days)
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
          Org benchmark recent window (days)
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

      <h3 className="mt-6 text-sm font-medium text-gray-900">Per-bureau window overrides</h3>
      <p className="mt-1 text-xs text-gray-500">
        Leave blank to use the org-wide windows above. Clearing both fields removes an override.
      </p>
      <div className="mt-3 space-y-3">
        {BUREAU_WINDOW_OPTIONS.map((bureau) => (
          <div
            key={bureau.value}
            className="grid grid-cols-1 gap-3 sm:grid-cols-[8rem_1fr_1fr] sm:items-end"
          >
            <p className="text-sm font-medium text-gray-700">{bureau.label}</p>
            <label className="block text-xs font-medium text-gray-700">
              Baseline days
              <input
                className={inputClass}
                type="number"
                min={7}
                max={365}
                placeholder="Org default"
                value={currentBureauDraft[bureau.value].baseline}
                onChange={(event) =>
                  setBureauDraft({
                    ...currentBureauDraft,
                    [bureau.value]: {
                      ...currentBureauDraft[bureau.value],
                      baseline: event.target.value,
                    },
                  })
                }
              />
            </label>
            <label className="block text-xs font-medium text-gray-700">
              Recent days
              <input
                className={inputClass}
                type="number"
                min={1}
                max={365}
                placeholder="Org default"
                value={currentBureauDraft[bureau.value].recent}
                onChange={(event) =>
                  setBureauDraft({
                    ...currentBureauDraft,
                    [bureau.value]: {
                      ...currentBureauDraft[bureau.value],
                      recent: event.target.value,
                    },
                  })
                }
              />
            </label>
          </div>
        ))}
      </div>

      <Button
        className="mt-4"
        disabled={save.isPending}
        onClick={() => {
          const bureauWindows: Record<string, BureauBenchmarkWindow | null> = {};
          for (const bureau of BUREAU_WINDOW_OPTIONS) {
            const baselineRaw = currentBureauDraft[bureau.value].baseline.trim();
            const recentRaw = currentBureauDraft[bureau.value].recent.trim();
            const hadOverride = Boolean(
              data.reinvestigation_benchmark_bureau_windows?.[bureau.value],
            );
            if (!baselineRaw && !recentRaw) {
              if (hadOverride) {
                bureauWindows[bureau.value] = null;
              }
              continue;
            }
            if (!baselineRaw || !recentRaw) {
              setFormError(`${bureau.label}: set both baseline and recent days, or clear both`);
              return;
            }
            const baseline = Number.parseInt(baselineRaw, 10);
            const recent = Number.parseInt(recentRaw, 10);
            if (!Number.isFinite(baseline) || !Number.isFinite(recent)) {
              setFormError(`${bureau.label}: window days must be numbers`);
              return;
            }
            if (recent > baseline) {
              setFormError(`${bureau.label}: recent days must be ≤ baseline days`);
              return;
            }
            bureauWindows[bureau.value] = { baseline_days: baseline, recent_days: recent };
          }
          setFormError(null);
          save.mutate({
            cross_bureau_balance_tolerance: currentTolerance,
            reinvestigation_benchmark_baseline_days: Number.parseInt(currentBaseline, 10),
            reinvestigation_benchmark_recent_days: Number.parseInt(currentRecent, 10),
            ...(Object.keys(bureauWindows).length > 0
              ? { reinvestigation_benchmark_bureau_windows: bureauWindows }
              : {}),
          });
        }}
      >
        {save.isPending ? 'Saving…' : 'Save dispute settings'}
      </Button>
      {formError ? <p className="mt-2 text-sm text-red-600">{formError}</p> : null}
      {save.isError && !formError ? (
        <p className="mt-2 text-sm text-red-600">Failed to save dispute settings.</p>
      ) : null}
    </Card>
  );
}
