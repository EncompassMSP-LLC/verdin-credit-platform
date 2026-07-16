import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getBureauResponseIngestionStatus,
  listBureauResponseIngestionRuns,
  startBureauResponseIngestionRun,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useAuth } from '../../lib/auth';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const BUREAU_TARGET_OPTIONS = [
  { value: 'all', label: 'All bureaus' },
  { value: 'equifax', label: 'Equifax' },
  { value: 'experian', label: 'Experian' },
  { value: 'transunion', label: 'TransUnion' },
];

const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function formatDate(value: string | null) {
  return value ? new Date(value).toLocaleString() : '—';
}

function statusBadgeVariant(status: string): 'default' | 'success' | 'warning' | 'danger' {
  if (status === 'deferred') return 'warning';
  if (status === 'failed') return 'danger';
  return 'default';
}

function optionalUuid(value: string): string | undefined {
  const trimmed = value.trim();
  return trimmed || undefined;
}

function isValidOptionalUuid(value: string): boolean {
  const trimmed = value.trim();
  return trimmed.length === 0 || UUID_RE.test(trimmed);
}

export function BureauResponseIngestionPanel() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const authReady = isAuthenticated && !authLoading;
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [summary, setSummary] = useState('');
  const [bureauTarget, setBureauTarget] = useState('all');
  const [startCaseId, setStartCaseId] = useState('');
  const [startAccountId, setStartAccountId] = useState('');
  const [filterCaseId, setFilterCaseId] = useState('');
  const [filterAccountId, setFilterAccountId] = useState('');
  const [appliedCaseId, setAppliedCaseId] = useState('');
  const [appliedAccountId, setAppliedAccountId] = useState('');
  const [formError, setFormError] = useState<string | null>(null);

  const statusQuery = useQuery({
    queryKey: ['bureau-response-ingestion-status'],
    queryFn: getBureauResponseIngestionStatus,
    enabled: authReady,
  });

  const runsQuery = useQuery({
    queryKey: ['bureau-response-ingestion-runs', page, appliedCaseId, appliedAccountId],
    queryFn: () =>
      listBureauResponseIngestionRuns({
        page,
        page_size: 20,
        case_id: optionalUuid(appliedCaseId),
        account_id: optionalUuid(appliedAccountId),
      }),
    enabled: authReady,
  });

  const startMutation = useMutation({
    mutationFn: startBureauResponseIngestionRun,
    onSuccess: async () => {
      setSummary('');
      setStartCaseId('');
      setStartAccountId('');
      setFormError(null);
      setPage(1);
      await queryClient.invalidateQueries({ queryKey: ['bureau-response-ingestion-runs'] });
      await queryClient.invalidateQueries({ queryKey: ['bureau-response-ingestion-status'] });
    },
    onError: (error: unknown) => {
      setFormError(error instanceof Error ? error.message : 'Failed to start ingestion audit run');
    },
  });

  if (authLoading || (authReady && (statusQuery.isLoading || runsQuery.isLoading))) {
    return (
      <Card>
        <p className="text-sm text-gray-500">Loading bureau response ingestion audit…</p>
      </Card>
    );
  }

  if (statusQuery.isError || runsQuery.isError) {
    return (
      <Card>
        <p className="text-sm text-red-600">Failed to load bureau response ingestion audit.</p>
        <Button
          type="button"
          variant="secondary"
          className="mt-3"
          onClick={() => {
            void statusQuery.refetch();
            void runsQuery.refetch();
          }}
        >
          Retry
        </Button>
      </Card>
    );
  }

  const status = statusQuery.data;
  const runs = runsQuery.data;
  const totalPages = runs ? Math.max(1, Math.ceil(runs.total / runs.page_size)) : 1;

  return (
    <div className="space-y-6">
      <Card title="Ingestion scaffold status">
        <p className="mb-3 text-sm text-gray-600">
          Operator-initiated audit runs record intent only. Live bureau polling stays deferred —
          starting a run always yields <code className="text-xs">status=deferred</code>.
        </p>
        {status ? (
          <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-gray-500">Enabled</dt>
              <dd>{status.enabled ? 'Yes' : 'No'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Ready for live polling</dt>
              <dd>{status.ready ? 'Yes' : 'No'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Live polling</dt>
              <dd>{status.live_polling_enabled ? 'Enabled' : 'Disabled'}</dd>
            </div>
          </dl>
        ) : null}
        {status && status.blockers.length > 0 ? (
          <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-gray-600">
            {status.blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        ) : null}
      </Card>

      <Card title="Start deferred audit run">
        <form
          className="space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            const trimmed = summary.trim();
            if (!trimmed) {
              setFormError('Summary is required');
              return;
            }
            if (!isValidOptionalUuid(startCaseId) || !isValidOptionalUuid(startAccountId)) {
              setFormError('Case ID and Account ID must be valid UUIDs when provided');
              return;
            }
            setFormError(null);
            startMutation.mutate({
              summary: trimmed,
              bureau_target: bureauTarget,
              case_id: optionalUuid(startCaseId) ?? null,
              account_id: optionalUuid(startAccountId) ?? null,
            });
          }}
        >
          <label className="block text-xs font-medium text-gray-700">
            Summary
            <textarea
              className={inputClass}
              rows={3}
              value={summary}
              placeholder="e.g. Quarterly Equifax response intake check for open cases"
              onChange={(event) => setSummary(event.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-gray-700">
            Bureau target
            <select
              className={inputClass}
              value={bureauTarget}
              onChange={(event) => setBureauTarget(event.target.value)}
            >
              {BUREAU_TARGET_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <label className="block text-xs font-medium text-gray-700">
              Case ID (optional)
              <input
                className={inputClass}
                value={startCaseId}
                placeholder="UUID"
                onChange={(event) => setStartCaseId(event.target.value)}
              />
            </label>
            <label className="block text-xs font-medium text-gray-700">
              Account ID (optional)
              <input
                className={inputClass}
                value={startAccountId}
                placeholder="UUID"
                onChange={(event) => setStartAccountId(event.target.value)}
              />
            </label>
          </div>
          {formError ? <p className="text-sm text-red-600">{formError}</p> : null}
          {startMutation.isSuccess ? (
            <p className="text-sm text-amber-700">
              Run recorded as deferred — no bureau API call was made.
            </p>
          ) : null}
          <Button type="submit" disabled={startMutation.isPending}>
            {startMutation.isPending ? 'Recording…' : 'Record deferred run'}
          </Button>
        </form>
      </Card>

      <Card title="Audit run history">
        <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <label className="block text-xs font-medium text-gray-700">
            Filter case ID
            <input
              className={inputClass}
              value={filterCaseId}
              placeholder="UUID"
              onChange={(event) => setFilterCaseId(event.target.value)}
            />
          </label>
          <label className="block text-xs font-medium text-gray-700">
            Filter account ID
            <input
              className={inputClass}
              value={filterAccountId}
              placeholder="UUID"
              onChange={(event) => setFilterAccountId(event.target.value)}
            />
          </label>
          <div className="flex items-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                if (!isValidOptionalUuid(filterCaseId) || !isValidOptionalUuid(filterAccountId)) {
                  return;
                }
                setAppliedCaseId(filterCaseId.trim());
                setAppliedAccountId(filterAccountId.trim());
                setPage(1);
              }}
            >
              Apply filters
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setFilterCaseId('');
                setFilterAccountId('');
                setAppliedCaseId('');
                setAppliedAccountId('');
                setPage(1);
              }}
            >
              Clear
            </Button>
          </div>
        </div>
        <div className="mb-3 flex items-center justify-between gap-4">
          <p className="text-sm text-gray-600">
            {runs ? `${runs.total} run(s)` : '—'} · page {page} of {totalPages}
          </p>
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={runsQuery.isFetching}
            onClick={() => void runsQuery.refetch()}
          >
            {runsQuery.isFetching ? 'Refreshing…' : 'Refresh'}
          </Button>
        </div>
        {!runs || runs.items.length === 0 ? (
          <p className="text-sm text-gray-500">
            No ingestion audit runs yet. Record a deferred run above to start the trail.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                  <th className="py-2 pr-4 font-medium">Requested</th>
                  <th className="py-2 pr-4 font-medium">Status</th>
                  <th className="py-2 pr-4 font-medium">Bureau</th>
                  <th className="py-2 pr-4 font-medium">Case</th>
                  <th className="py-2 pr-4 font-medium">Account</th>
                  <th className="py-2 pr-4 font-medium">Summary</th>
                  <th className="py-2 font-medium">Deferral</th>
                </tr>
              </thead>
              <tbody>
                {runs.items.map((run) => (
                  <tr key={run.id} className="border-b border-gray-100 align-top">
                    <td className="py-2 pr-4 whitespace-nowrap">{formatDate(run.requested_at)}</td>
                    <td className="py-2 pr-4">
                      <Badge variant={statusBadgeVariant(run.status)}>{run.status}</Badge>
                    </td>
                    <td className="py-2 pr-4">{run.bureau_target}</td>
                    <td className="py-2 pr-4 font-mono text-xs">{run.case_id ?? '—'}</td>
                    <td className="py-2 pr-4 font-mono text-xs">{run.account_id ?? '—'}</td>
                    <td className="max-w-xs py-2 pr-4">{run.summary}</td>
                    <td className="max-w-sm py-2 text-gray-600">{run.deferral_reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {runs && runs.total > runs.page_size ? (
          <div className="mt-4 flex gap-2">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
            >
              Previous
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
            >
              Next
            </Button>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
