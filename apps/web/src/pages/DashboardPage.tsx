import { useQuery } from '@tanstack/react-query';
import { getDashboard } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { useAuth } from '../lib/auth';
import { AiReadiness } from '../components/dashboard/AiReadiness';
import { BusinessMetrics } from '../components/dashboard/BusinessMetrics';
import { KpiRow } from '../components/dashboard/KpiRow';
import { ProcessingHealth } from '../components/dashboard/ProcessingHealth';
import { TimelineFeed } from '../components/dashboard/TimelineFeed';
import { WorkQueuePanel } from '../components/dashboard/WorkQueuePanel';

function formatGeneratedAt(value: string) {
  return new Date(value).toLocaleString();
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
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Operations Command Center</h1>
          <p className="mt-1 text-gray-500">
            Welcome back, {user?.first_name}. What is happening, what needs attention, and how the
            business is performing — at a glance.
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
          <p className="py-12 text-center text-sm text-gray-500">Loading operations snapshot…</p>
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
          <KpiRow kpis={data.kpis} />

          <section aria-label="Operational work queue">
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
              What Needs Attention
            </h2>
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
              <WorkQueuePanel
                title="Overdue Tasks"
                items={data.tasks.overdue_tasks}
                emptyMessage="No overdue tasks."
              />
              <WorkQueuePanel
                title="High Priority Cases"
                items={data.tasks.high_priority_cases}
                emptyMessage="No high-priority open cases."
              />
              <WorkQueuePanel
                title="Documents Requiring Review"
                items={data.tasks.documents_requiring_review}
                emptyMessage="No ambiguous entity matches awaiting review."
              />
              <WorkQueuePanel
                title="OCR Failures"
                items={data.tasks.ocr_failures}
                emptyMessage="No OCR failures."
              />
              <WorkQueuePanel
                title="Unresolved Entity Matches"
                items={data.tasks.unresolved_entity_matches}
                emptyMessage="No unresolved entity matches."
              />
            </div>
          </section>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            <ProcessingHealth processing={data.processing} />
            <AiReadiness ai={data.ai} />
          </div>

          <TimelineFeed items={data.timeline} />

          <BusinessMetrics performance={data.performance} />
        </div>
      ) : null}
    </div>
  );
}
