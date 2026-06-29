import { useQuery } from '@tanstack/react-query';
import { getDashboard } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useAuth } from '../lib/auth';
import { AlertsPanel } from '../components/dashboard/AlertsPanel';
import { DashboardMetricCard } from '../components/dashboard/DashboardMetricCard';
import { DashboardSection } from '../components/dashboard/DashboardSection';
import { MissionControlOverview } from '../components/dashboard/MissionControlOverview';
import { TimelineFeed } from '../components/dashboard/TimelineFeed';

function formatGeneratedAt(value: string) {
  return new Date(value).toLocaleString();
}

function formatHours(value: number | null) {
  return value != null ? `${value}h` : '—';
}

function formatConfidence(value: number | null) {
  return value != null ? `${(value * 100).toFixed(1)}%` : '—';
}

export function DashboardPage() {
  const { user } = useAuth();

  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
    refetchInterval: (query) => (query.state.data?.refresh_seconds ?? 30) * 1000,
  });

  const refreshSeconds = data?.refresh_seconds ?? 30;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">
            Mission Control
          </p>
          <h1 className="mt-1 text-3xl font-bold text-gray-900">Operations Command Center</h1>
          <p className="mt-2 max-w-3xl text-gray-600">
            Welcome back, {user?.first_name}. One live snapshot of what is happening, what needs
            attention, and how the business is performing.
          </p>
          {data ? (
            <p className="mt-2 text-xs text-gray-400">
              Snapshot {formatGeneratedAt(data.generated_at)}
              {isFetching ? ' · refreshing…' : ` · auto-refresh every ${refreshSeconds}s`}
            </p>
          ) : null}
        </div>
        <Button variant="secondary" onClick={() => refetch()} disabled={isFetching}>
          {isFetching ? 'Refreshing…' : 'Refresh now'}
        </Button>
      </div>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading mission control…</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <p className="py-8 text-center text-sm text-red-600">
            Failed to load dashboard: {error instanceof Error ? error.message : 'Unknown error'}
          </p>
          <div className="flex justify-center pb-4">
            <Button onClick={() => refetch()}>Retry</Button>
          </div>
        </Card>
      ) : null}

      {data ? (
        <div className="space-y-8">
          <MissionControlOverview overview={data.overview} />

          <div className="grid grid-cols-1 gap-8 xl:grid-cols-2">
            <DashboardSection title="Operations" description="Workload across the platform.">
              <DashboardMetricCard
                label="Open Cases"
                value={data.overview.open_cases}
                tone="info"
              />
              <DashboardMetricCard
                label="Active Accounts"
                value={data.overview.active_accounts}
                tone="success"
              />
              <DashboardMetricCard label="Documents" value={data.overview.documents} />
              <DashboardMetricCard
                label="Tasks Due Today"
                value={data.tasks.due_today}
                tone="warning"
              />
              <DashboardMetricCard label="Overdue Tasks" value={data.tasks.overdue} tone="danger" />
            </DashboardSection>

            <DashboardSection title="Processing" description="Document pipeline health.">
              <DashboardMetricCard label="OCR Queue" value={data.processing.ocr_queue} />
              <DashboardMetricCard
                label="OCR Failed"
                value={data.processing.ocr_failed}
                tone={data.processing.ocr_failed > 0 ? 'danger' : 'default'}
              />
              <DashboardMetricCard
                label="Classification Pending"
                value={data.processing.classification_pending}
              />
              <DashboardMetricCard
                label="Metadata Pending"
                value={data.processing.metadata_pending}
              />
              <DashboardMetricCard
                label="Entity Resolution Pending"
                value={data.processing.entity_resolution_pending}
              />
            </DashboardSection>

            <DashboardSection title="Performance" description="Business throughput today.">
              <DashboardMetricCard
                label="Cases Created Today"
                value={data.performance.cases_created_today}
              />
              <DashboardMetricCard
                label="Cases Closed"
                value={data.performance.cases_closed_today}
              />
              <DashboardMetricCard
                label="Avg Resolution Time"
                value={formatHours(data.performance.average_resolution_time_hours)}
              />
              <DashboardMetricCard
                label="Documents Per Case"
                value={data.performance.documents_per_case}
              />
              <DashboardMetricCard
                label="Accounts Per Case"
                value={data.performance.accounts_per_case}
              />
            </DashboardSection>

            <DashboardSection title="Intelligence" description="Document AI readiness.">
              <DashboardMetricCard
                label="Classification Confidence"
                value={formatConfidence(data.documents.classification_confidence)}
              />
              <DashboardMetricCard
                label="Entity Resolution Confidence"
                value={formatConfidence(data.documents.entity_resolution_confidence)}
              />
              <DashboardMetricCard label="AI Ready Documents" value={data.documents.ai_ready} />
              <DashboardMetricCard
                label="Unresolved Documents"
                value={data.documents.unresolved}
                tone={data.documents.unresolved > 0 ? 'warning' : 'default'}
              />
              <DashboardMetricCard label="Processing" value={data.documents.processing} />
            </DashboardSection>
          </div>

          <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
            <div className="xl:col-span-2">
              <TimelineFeed items={data.timeline} />
            </div>
            <AlertsPanel alerts={data.alerts.items} total={data.alerts.total} />
          </div>
        </div>
      ) : null}
    </div>
  );
}
