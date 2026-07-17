import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  getBureauPerformanceReporting,
  getEnterpriseReportingStatus,
  getOperationsReporting,
  getReinvestigationOutcomeAnalytics,
  getReinvestigationOutcomeBenchmarks,
  getRevenueAnalyticsReporting,
  getTeamProductivityReporting,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { DashboardMetricCard } from '../../components/dashboard/DashboardMetricCard';
import { featureFlags } from '../../lib/feature-flags';

type ReportingTab = 'operations' | 'bureau' | 'team' | 'reinvestigation' | 'benchmarks' | 'revenue';

function formatPercent(rate: number) {
  return `${(rate * 100).toFixed(1)}%`;
}

function formatSignedPercent(rate: number) {
  const pct = (rate * 100).toFixed(1);
  if (rate > 0) return `+${pct}%`;
  if (rate < 0) return `${pct}%`;
  return `${pct}%`;
}

function formatGeneratedAt(value: string) {
  return new Date(value).toLocaleString();
}

function formatLabel(value: string) {
  return value.replaceAll('_', ' ');
}

function StatusBreakdown({ title, counts }: { title: string; counts: Record<string, number> }) {
  const entries = Object.entries(counts).filter(([, count]) => count > 0);
  if (entries.length === 0) {
    return null;
  }

  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700">{title}</h3>
      <ul className="mt-2 space-y-2">
        {entries.map(([status, count]) => (
          <li
            key={status}
            className="flex items-center justify-between rounded-md border border-gray-200 px-4 py-2 text-sm"
          >
            <span className="capitalize text-gray-700">{formatLabel(status)}</span>
            <span className="font-medium text-gray-900">{count}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ReportingCenterPage() {
  const [tab, setTab] = useState<ReportingTab>('operations');

  if (!featureFlags.enableEnterprise) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">
            Enterprise reporting requires{' '}
            <code className="text-xs">VITE_ENABLE_ENTERPRISE=true</code>.
          </p>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Enterprise reporting</h1>
        <p className="mt-1 text-gray-500">
          Operations KPIs, bureau performance, team productivity, reinvestigation outcomes, and
          org-internal baselines.
        </p>
      </div>

      <ReportingStatusCard />

      <div className="mb-6 flex flex-wrap gap-2">
        <Button
          type="button"
          variant={tab === 'operations' ? 'primary' : 'secondary'}
          onClick={() => setTab('operations')}
        >
          Operations
        </Button>
        <Button
          type="button"
          variant={tab === 'bureau' ? 'primary' : 'secondary'}
          onClick={() => setTab('bureau')}
        >
          Bureau performance
        </Button>
        <Button
          type="button"
          variant={tab === 'team' ? 'primary' : 'secondary'}
          onClick={() => setTab('team')}
        >
          Team productivity
        </Button>
        <Button
          type="button"
          variant={tab === 'reinvestigation' ? 'primary' : 'secondary'}
          onClick={() => setTab('reinvestigation')}
        >
          Reinvestigation outcomes
        </Button>
        <Button
          type="button"
          variant={tab === 'benchmarks' ? 'primary' : 'secondary'}
          onClick={() => setTab('benchmarks')}
        >
          Outcome benchmarks
        </Button>
        <Button
          type="button"
          variant={tab === 'revenue' ? 'primary' : 'secondary'}
          onClick={() => setTab('revenue')}
        >
          Revenue readiness
        </Button>
      </div>

      {tab === 'operations' ? <OperationsPanel /> : null}
      {tab === 'bureau' ? <BureauPerformancePanel /> : null}
      {tab === 'team' ? <TeamProductivityPanel /> : null}
      {tab === 'reinvestigation' ? <ReinvestigationOutcomesPanel /> : null}
      {tab === 'benchmarks' ? <ReinvestigationBenchmarksPanel /> : null}
      {tab === 'revenue' ? <RevenueAnalyticsPanel /> : null}
    </div>
  );
}

function ReportingStatusCard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['reporting-status'],
    queryFn: getEnterpriseReportingStatus,
  });

  if (isLoading) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-gray-500">Loading reporting status…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card className="mb-6">
        <p className="text-sm text-red-600">Failed to load enterprise reporting status.</p>
      </Card>
    );
  }

  return (
    <Card className="mb-6" title="Capabilities">
      <div className="flex flex-wrap gap-2">
        {data.capabilities.map((capability) => (
          <Badge key={capability} variant="success">
            {formatLabel(capability)}
          </Badge>
        ))}
        {data.deferred_capabilities.map((capability) => (
          <Badge key={capability} variant="default">
            {formatLabel(capability)} (deferred)
          </Badge>
        ))}
      </div>
    </Card>
  );
}

function OperationsPanel() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-operations'],
    queryFn: getOperationsReporting,
  });

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-gray-500">Loading operations reporting…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card>
        <p className="text-sm text-red-600">
          Failed to load operations reporting:{' '}
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
        <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
          Retry
        </Button>
      </Card>
    );
  }

  const ops = data.operations;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <p className="text-xs text-gray-400">Generated {formatGeneratedAt(data.generated_at)}</p>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <DashboardMetricCard label="Total clients" value={ops.clients.total} />
        <DashboardMetricCard label="Active clients" value={ops.clients.active} tone="success" />
        <DashboardMetricCard
          label="Portal enabled"
          value={ops.clients.portal_enabled}
          tone="info"
        />
        <DashboardMetricCard label="Portal users" value={ops.portal_users} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title="Notifications">
          <div className="grid grid-cols-2 gap-4">
            <DashboardMetricCard
              label="Unread"
              value={ops.notifications.unread_total}
              tone="warning"
            />
            <DashboardMetricCard label="Created today" value={ops.notifications.created_today} />
          </div>
        </Card>

        <Card title="Dispute breakdown">
          <div className="space-y-4">
            <StatusBreakdown title="Accounts by dispute status" counts={ops.dispute_accounts} />
            <StatusBreakdown title="Letters by status" counts={ops.dispute_letters} />
          </div>
        </Card>
      </div>
    </div>
  );
}

function BureauPerformancePanel() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-bureau-performance'],
    queryFn: getBureauPerformanceReporting,
  });

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-gray-500">Loading bureau performance…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card>
        <p className="text-sm text-red-600">
          Failed to load bureau performance:{' '}
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
        <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
          Retry
        </Button>
      </Card>
    );
  }

  const report = data.bureau_performance;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-gray-600">
          {report.total_accounts} accounts across {report.bureaus.length} bureaus · generated{' '}
          {formatGeneratedAt(data.generated_at)}
        </p>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      {report.bureaus.length === 0 ? (
        <Card>
          <p className="text-sm text-gray-500">No bureau performance data yet.</p>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Bureau</th>
                  <th className="px-3 py-2 font-medium">Accounts</th>
                  <th className="px-3 py-2 font-medium">Sent letters</th>
                  <th className="px-3 py-2 font-medium">Resolved</th>
                  <th className="px-3 py-2 font-medium">Dispute status</th>
                </tr>
              </thead>
              <tbody>
                {report.bureaus.map((item) => (
                  <tr key={item.bureau} className="border-b border-gray-100 align-top">
                    <td className="px-3 py-3 font-medium capitalize text-gray-900">
                      {formatLabel(item.bureau)}
                    </td>
                    <td className="px-3 py-3">{item.total_accounts}</td>
                    <td className="px-3 py-3">{item.sent_letters}</td>
                    <td className="px-3 py-3">{item.resolved_accounts}</td>
                    <td className="px-3 py-3">
                      <ul className="space-y-1">
                        {Object.entries(item.dispute_status).map(([status, count]) => (
                          <li key={status} className="text-gray-600">
                            <span className="capitalize">{formatLabel(status)}</span>: {count}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

function TeamProductivityPanel() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-team-productivity'],
    queryFn: getTeamProductivityReporting,
  });

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-gray-500">Loading team productivity…</p>
      </Card>
    );
  }

  if (isError || !data) {
    return (
      <Card>
        <p className="text-sm text-red-600">
          Failed to load team productivity:{' '}
          {error instanceof Error ? error.message : 'Unknown error'}
        </p>
        <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
          Retry
        </Button>
      </Card>
    );
  }

  const report = data.team_productivity;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <p className="text-xs text-gray-400">Generated {formatGeneratedAt(data.generated_at)}</p>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <DashboardMetricCard label="Open tasks" value={report.open_tasks_total} tone="warning" />
        <DashboardMetricCard
          label="Completed tasks (30d)"
          value={report.completed_tasks_30d_total}
          tone="success"
        />
        <DashboardMetricCard label="Open cases assigned" value={report.assigned_open_cases_total} />
        <DashboardMetricCard
          label="Cases closed (30d)"
          value={report.closed_cases_30d_total}
          tone="info"
        />
      </div>

      {report.members.length === 0 ? (
        <Card>
          <p className="text-sm text-gray-500">No team productivity data yet.</p>
        </Card>
      ) : (
        <Card title="By team member">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-gray-500">
                  <th className="px-3 py-2 font-medium">Member</th>
                  <th className="px-3 py-2 font-medium">Open tasks</th>
                  <th className="px-3 py-2 font-medium">Completed (30d)</th>
                  <th className="px-3 py-2 font-medium">Open cases</th>
                  <th className="px-3 py-2 font-medium">Closed (30d)</th>
                </tr>
              </thead>
              <tbody>
                {report.members.map((member) => (
                  <tr key={member.user_id} className="border-b border-gray-100">
                    <td className="px-3 py-3">
                      <p className="font-medium text-gray-900">{member.full_name}</p>
                      <p className="text-xs text-gray-500">{member.email}</p>
                    </td>
                    <td className="px-3 py-3">{member.open_tasks}</td>
                    <td className="px-3 py-3">{member.completed_tasks_30d}</td>
                    <td className="px-3 py-3">{member.assigned_open_cases}</td>
                    <td className="px-3 py-3">{member.closed_cases_30d}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}

const REINVESTIGATION_BUREAU_OPTIONS = [
  { value: '', label: 'All bureaus' },
  { value: 'equifax', label: 'Equifax' },
  { value: 'experian', label: 'Experian' },
  { value: 'transunion', label: 'TransUnion' },
];

function ReinvestigationOutcomesPanel() {
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [bureau, setBureau] = useState('');
  const [groupBy, setGroupBy] = useState<'bureau' | 'recipient'>('bureau');

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-reinvestigation-outcomes', start, end, bureau, groupBy],
    queryFn: () =>
      getReinvestigationOutcomeAnalytics({
        start: start || undefined,
        end: end || undefined,
        bureau: bureau || undefined,
        group_by: groupBy,
      }),
  });

  const filterControls = (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <label className="text-xs font-medium text-gray-700">
        From (response date)
        <input
          type="date"
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={start}
          max={end || undefined}
          onChange={(event) => setStart(event.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-gray-700">
        To (response date)
        <input
          type="date"
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={end}
          min={start || undefined}
          onChange={(event) => setEnd(event.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-gray-700">
        Bureau
        <select
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={bureau}
          onChange={(event) => setBureau(event.target.value)}
        >
          {REINVESTIGATION_BUREAU_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
      <label className="text-xs font-medium text-gray-700">
        Break down by
        <select
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={groupBy}
          onChange={(event) => setGroupBy(event.target.value as 'bureau' | 'recipient')}
        >
          <option value="bureau">Bureau</option>
          <option value="recipient">Recipient</option>
        </select>
      </label>
    </div>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>{filterControls}</Card>
        <Card>
          <p className="text-sm text-gray-500">Loading reinvestigation outcomes…</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-6">
        <Card>{filterControls}</Card>
        <Card>
          <p className="text-sm text-red-600">
            Failed to load reinvestigation outcomes:{' '}
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  const analytics = data.analytics;

  return (
    <div className="space-y-6">
      <Card>{filterControls}</Card>
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-gray-600">
          {analytics.total_responses} recorded response(s) · generated{' '}
          {formatGeneratedAt(data.generated_at)}
        </p>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      {analytics.total_responses === 0 ? (
        <Card>
          <p className="text-sm text-gray-500">
            No dispute responses recorded yet. Outcome trends appear once staff log bureau
            responses.
          </p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <DashboardMetricCard
              label="Deletion rate"
              value={formatPercent(analytics.deletion_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Favorable rate"
              value={formatPercent(analytics.favorable_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Verification rate"
              value={formatPercent(analytics.verification_rate)}
              tone="warning"
            />
            <DashboardMetricCard
              label="Avg days to response"
              value={
                analytics.avg_days_to_response === null
                  ? '—'
                  : String(analytics.avg_days_to_response)
              }
              tone="info"
            />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <Card title="Outcome breakdown">
              <StatusBreakdown title="Recorded responses by outcome" counts={analytics.counts} />
            </Card>
            <Card title="Time to response">
              <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-gray-500">Average days</dt>
                  <dd>{analytics.avg_days_to_response ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Median days</dt>
                  <dd>{analytics.median_days_to_response ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Correction rate</dt>
                  <dd>{formatPercent(analytics.correction_rate)}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">No-response rate</dt>
                  <dd>{formatPercent(analytics.no_response_rate)}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Measured responses</dt>
                  <dd>{analytics.measured_response_count}</dd>
                </div>
              </dl>
            </Card>
          </div>

          {data.by_bureau.length > 0 ? (
            <Card title="Per-bureau breakdown">
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                      <th className="py-2 pr-4 font-medium">Bureau</th>
                      <th className="py-2 pr-4 font-medium">Responses</th>
                      <th className="py-2 pr-4 font-medium">Deletion</th>
                      <th className="py-2 pr-4 font-medium">Favorable</th>
                      <th className="py-2 pr-4 font-medium">Verification</th>
                      <th className="py-2 font-medium">Avg days</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_bureau.map((item) => (
                      <tr key={item.bureau} className="border-b border-gray-100">
                        <td className="py-2 pr-4 font-medium text-gray-900">
                          {formatLabel(item.bureau)}
                        </td>
                        <td className="py-2 pr-4">{item.analytics.total_responses}</td>
                        <td className="py-2 pr-4">{formatPercent(item.analytics.deletion_rate)}</td>
                        <td className="py-2 pr-4">
                          {formatPercent(item.analytics.favorable_rate)}
                        </td>
                        <td className="py-2 pr-4">
                          {formatPercent(item.analytics.verification_rate)}
                        </td>
                        <td className="py-2">
                          {item.analytics.avg_days_to_response === null
                            ? '—'
                            : String(item.analytics.avg_days_to_response)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          ) : null}

          {data.by_recipient.length > 0 ? (
            <Card title="Per-recipient breakdown">
              <div className="overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead>
                    <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                      <th className="py-2 pr-4 font-medium">Recipient</th>
                      <th className="py-2 pr-4 font-medium">Responses</th>
                      <th className="py-2 pr-4 font-medium">Deletion</th>
                      <th className="py-2 pr-4 font-medium">Favorable</th>
                      <th className="py-2 pr-4 font-medium">Verification</th>
                      <th className="py-2 font-medium">Avg days</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_recipient.map((item) => (
                      <tr key={item.recipient} className="border-b border-gray-100">
                        <td className="py-2 pr-4 font-medium text-gray-900">
                          {formatLabel(item.recipient)}
                        </td>
                        <td className="py-2 pr-4">{item.analytics.total_responses}</td>
                        <td className="py-2 pr-4">{formatPercent(item.analytics.deletion_rate)}</td>
                        <td className="py-2 pr-4">
                          {formatPercent(item.analytics.favorable_rate)}
                        </td>
                        <td className="py-2 pr-4">
                          {formatPercent(item.analytics.verification_rate)}
                        </td>
                        <td className="py-2">
                          {item.analytics.avg_days_to_response === null
                            ? '—'
                            : String(item.analytics.avg_days_to_response)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          ) : null}
        </>
      )}
    </div>
  );
}

function ReinvestigationBenchmarksPanel() {
  const [baselineOverride, setBaselineOverride] = useState<string | null>(null);
  const [recentOverride, setRecentOverride] = useState<string | null>(null);
  const [bureau, setBureau] = useState('');

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-reinvestigation-benchmarks', baselineOverride, recentOverride, bureau],
    queryFn: () =>
      getReinvestigationOutcomeBenchmarks({
        baseline_days:
          baselineOverride != null ? Number.parseInt(baselineOverride, 10) || undefined : undefined,
        recent_days:
          recentOverride != null ? Number.parseInt(recentOverride, 10) || undefined : undefined,
        bureau: bureau || undefined,
        group_by: 'bureau',
      }),
  });

  const displayBaseline =
    baselineOverride ?? (data ? String(data.baseline_period.window_days) : '');
  const displayRecent = recentOverride ?? (data ? String(data.recent_period.window_days) : '');

  const filterControls = (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <label className="text-xs font-medium text-gray-700">
        Baseline window (days)
        <input
          type="number"
          min={7}
          max={365}
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={displayBaseline}
          placeholder="Org default"
          onChange={(event) => setBaselineOverride(event.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-gray-700">
        Recent window (days)
        <input
          type="number"
          min={1}
          max={365}
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={displayRecent}
          placeholder="Org default"
          onChange={(event) => setRecentOverride(event.target.value)}
        />
      </label>
      <label className="text-xs font-medium text-gray-700">
        Bureau
        <select
          className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          value={bureau}
          onChange={(event) => setBureau(event.target.value)}
        >
          {REINVESTIGATION_BUREAU_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  );

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>{filterControls}</Card>
        <Card>
          <p className="text-sm text-gray-500">Loading org-internal outcome benchmarks…</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="space-y-6">
        <Card>{filterControls}</Card>
        <Card>
          <p className="text-sm text-red-600">
            Failed to load outcome benchmarks:{' '}
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        </Card>
      </div>
    );
  }

  const { baseline, recent, rate_deltas: deltas, baseline_period, recent_period } = data;

  return (
    <div className="space-y-6">
      <Card>{filterControls}</Card>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1 text-sm text-gray-600">
          <p>
            Org-scoped only ({data.scope}) · generated {formatGeneratedAt(data.generated_at)}
          </p>
          <p>
            Baseline {baseline_period.start} → {baseline_period.end} ({baseline_period.window_days}
            d) · Recent {recent_period.start} → {recent_period.end} ({recent_period.window_days}d)
          </p>
        </div>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      <Card title="Advisory rate deltas (recent − baseline)">
        <p className="mb-4 text-xs text-gray-500">
          Positive means the recent window is higher than the trailing baseline. Comparison uses
          this organization&apos;s recorded responses only — no cross-tenant data.
        </p>
        <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
          <DashboardMetricCard
            label="Deletion Δ"
            value={formatSignedPercent(deltas.deletion_rate)}
            tone={deltas.deletion_rate >= 0 ? 'success' : 'warning'}
          />
          <DashboardMetricCard
            label="Favorable Δ"
            value={formatSignedPercent(deltas.favorable_rate)}
            tone={deltas.favorable_rate >= 0 ? 'success' : 'warning'}
          />
          <DashboardMetricCard
            label="Verification Δ"
            value={formatSignedPercent(deltas.verification_rate)}
            tone="info"
          />
          <DashboardMetricCard
            label="Correction Δ"
            value={formatSignedPercent(deltas.correction_rate)}
            tone="info"
          />
          <DashboardMetricCard
            label="No-response Δ"
            value={formatSignedPercent(deltas.no_response_rate)}
            tone={deltas.no_response_rate <= 0 ? 'success' : 'warning'}
          />
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card title={`Baseline (${baseline_period.window_days}d)`}>
          <p className="mb-3 text-sm text-gray-600">{baseline.total_responses} response(s)</p>
          <div className="mb-4 grid grid-cols-2 gap-3">
            <DashboardMetricCard
              label="Deletion rate"
              value={formatPercent(baseline.deletion_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Favorable rate"
              value={formatPercent(baseline.favorable_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Verification rate"
              value={formatPercent(baseline.verification_rate)}
              tone="warning"
            />
            <DashboardMetricCard
              label="Avg days"
              value={
                baseline.avg_days_to_response === null ? '—' : String(baseline.avg_days_to_response)
              }
              tone="info"
            />
          </div>
          <StatusBreakdown title="Baseline outcomes" counts={baseline.counts} />
        </Card>
        <Card title={`Recent (${recent_period.window_days}d)`}>
          <p className="mb-3 text-sm text-gray-600">{recent.total_responses} response(s)</p>
          <div className="mb-4 grid grid-cols-2 gap-3">
            <DashboardMetricCard
              label="Deletion rate"
              value={formatPercent(recent.deletion_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Favorable rate"
              value={formatPercent(recent.favorable_rate)}
              tone="success"
            />
            <DashboardMetricCard
              label="Verification rate"
              value={formatPercent(recent.verification_rate)}
              tone="warning"
            />
            <DashboardMetricCard
              label="Avg days"
              value={
                recent.avg_days_to_response === null ? '—' : String(recent.avg_days_to_response)
              }
              tone="info"
            />
          </div>
          <StatusBreakdown title="Recent outcomes" counts={recent.counts} />
        </Card>
      </div>

      {data.by_bureau.length > 0 ? (
        <Card title="Per-bureau breakdown">
          <p className="mb-3 text-xs text-gray-500">
            Same baseline/recent windows as the org aggregate. Deletion Δ is recent − baseline for
            each bureau.
          </p>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-200 text-xs uppercase tracking-wide text-gray-500">
                  <th className="py-2 pr-4 font-medium">Bureau</th>
                  <th className="py-2 pr-4 font-medium">Baseline resp.</th>
                  <th className="py-2 pr-4 font-medium">Recent resp.</th>
                  <th className="py-2 pr-4 font-medium">Deletion Δ</th>
                  <th className="py-2 pr-4 font-medium">Favorable Δ</th>
                  <th className="py-2 font-medium">Recent deletion</th>
                </tr>
              </thead>
              <tbody>
                {data.by_bureau.map((item) => (
                  <tr key={item.bureau} className="border-b border-gray-100">
                    <td className="py-2 pr-4 font-medium text-gray-900">
                      {formatLabel(item.bureau)}
                    </td>
                    <td className="py-2 pr-4">{item.baseline.total_responses}</td>
                    <td className="py-2 pr-4">{item.recent.total_responses}</td>
                    <td className="py-2 pr-4">
                      {formatSignedPercent(item.rate_deltas.deletion_rate)}
                    </td>
                    <td className="py-2 pr-4">
                      {formatSignedPercent(item.rate_deltas.favorable_rate)}
                    </td>
                    <td className="py-2">{formatPercent(item.recent.deletion_rate)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : null}
    </div>
  );
}

function RevenueAnalyticsPanel() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reporting-revenue'],
    queryFn: getRevenueAnalyticsReporting,
    retry: false,
  });

  if (isLoading) {
    return (
      <Card>
        <p className="text-sm text-gray-500">Loading revenue analytics…</p>
      </Card>
    );
  }

  if (isError || !data) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    const billingDisabled =
      message.toLowerCase().includes('billing is not enabled') ||
      message.toLowerCase().includes('not found') ||
      message.includes('404');
    return (
      <Card>
        <p className="text-sm text-gray-600">
          {billingDisabled
            ? 'Revenue analytics requires ENABLE_BILLING=true and Stripe configuration in the API environment.'
            : `Failed to load revenue analytics: ${message}`}
        </p>
        {!billingDisabled ? (
          <Button className="mt-4" variant="secondary" onClick={() => refetch()}>
            Retry
          </Button>
        ) : null}
      </Card>
    );
  }

  const analytics = data.revenue_analytics;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-gray-600">
          Readiness score {analytics.readiness_score}/100 · generated{' '}
          {formatGeneratedAt(data.generated_at)}
        </p>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh'}
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <DashboardMetricCard
          label="Readiness score"
          value={analytics.readiness_score}
          tone={analytics.readiness_score >= 70 ? 'success' : 'warning'}
        />
        <DashboardMetricCard
          label="Subscription"
          value={
            analytics.subscription_active ? 'Active' : formatLabel(analytics.subscription_status)
          }
          tone={analytics.subscription_active ? 'success' : 'default'}
        />
        <DashboardMetricCard label="Active clients" value={analytics.active_clients} />
        <DashboardMetricCard label="Portal users" value={analytics.portal_users} />
      </div>

      <Card title="Billing readiness">
        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-gray-500">Billing ready</dt>
            <dd>{analytics.billing_ready ? 'Yes' : 'No'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Stripe customer</dt>
            <dd>{analytics.stripe_customer_configured ? 'Configured' : 'Not configured'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Subscription record</dt>
            <dd>{analytics.stripe_subscription_configured ? 'Configured' : 'Not configured'}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Renewal within 30 days</dt>
            <dd>
              {analytics.renewal_within_30_days === null
                ? '—'
                : analytics.renewal_within_30_days
                  ? 'Yes'
                  : 'No'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Portal-enabled clients</dt>
            <dd>{analytics.portal_enabled_clients}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Price ID</dt>
            <dd className="break-all font-mono text-xs">{analytics.price_id ?? '—'}</dd>
          </div>
        </dl>
      </Card>
    </div>
  );
}
