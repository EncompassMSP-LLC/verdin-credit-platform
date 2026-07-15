import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseReinvestigationSummary,
  type AccountRedisputeReadiness,
  type RedisputeAction,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';

const ACTION_LABELS: Record<RedisputeAction, string> = {
  wait: 'Await response',
  prepare_initial: 'Prepare dispute',
  redispute: 'Re-dispute',
  escalate_cfpb: 'Escalate (CFPB)',
  escalate_attorney: 'Escalate (attorney)',
  resolved: 'Resolved',
};

function Stat({ label, value, tone }: { label: string; value: string | number; tone?: string }) {
  return (
    <div className="rounded-md border border-gray-200 px-3 py-2">
      <p className={`text-lg font-semibold ${tone ?? 'text-gray-900'}`}>{value}</p>
      <p className="mt-0.5 text-xs text-gray-500">{label}</p>
    </div>
  );
}

function ActionItem({ item }: { item: AccountRedisputeReadiness }) {
  return (
    <li className="flex flex-wrap items-start justify-between gap-2 rounded-md border border-gray-200 px-3 py-2">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900">{item.creditor_name}</p>
        <p className="mt-0.5 text-xs text-gray-600">{item.reason}</p>
      </div>
      <Badge variant="danger">{ACTION_LABELS[item.action]}</Badge>
    </li>
  );
}

export function CaseReinvestigationSummaryCard({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const summaryQuery = useQuery({
    queryKey: ['case-reinvestigation-summary', caseId],
    queryFn: () => getCaseReinvestigationSummary(caseId),
    retry: false,
  });

  const summary = summaryQuery.data;
  const actionItems = summary?.action_items ?? [];

  return (
    <div id={id} className={className}>
      <Card title="Reinvestigation overview">
        <p className="text-sm text-gray-500">
          Case-wide roll-up of the FCRA §611 clock, recorded responses, and advisory next steps.
          Read-only — no live bureau contact.
        </p>

        {summaryQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading reinvestigation overview…</p>
        ) : null}

        {summaryQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {summaryQuery.error instanceof ApiClientError
              ? summaryQuery.error.message
              : 'Failed to load reinvestigation overview'}
          </p>
        ) : null}

        {summary ? (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-5">
              <Stat
                label="Overdue"
                value={summary.clock.overdue}
                tone={summary.clock.overdue > 0 ? 'text-red-600' : 'text-gray-900'}
              />
              <Stat
                label="Due soon"
                value={summary.clock.due_soon}
                tone={summary.clock.due_soon > 0 ? 'text-amber-600' : 'text-gray-900'}
              />
              <Stat
                label="High-priority actions"
                value={summary.readiness.high_priority}
                tone={summary.readiness.high_priority > 0 ? 'text-red-600' : 'text-gray-900'}
              />
              <Stat label="Responses recorded" value={summary.total_responses} />
              <Stat label="Disputed tradelines" value={summary.disputed_accounts} />
            </div>

            <div className="flex flex-wrap gap-4 text-xs text-gray-500">
              {summary.next_deadline ? (
                <span>
                  Next deadline: {new Date(summary.next_deadline).toLocaleDateString()}
                  {summary.next_deadline_creditor ? ` (${summary.next_deadline_creditor})` : ''}
                </span>
              ) : (
                <span>No upcoming reinvestigation deadlines.</span>
              )}
              {summary.most_overdue_days !== null ? (
                <span className="text-red-600">
                  Most overdue: {summary.most_overdue_days}d past deadline
                </span>
              ) : null}
            </div>

            {actionItems.length > 0 ? (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  Recommended actions
                </p>
                <ul className="space-y-2">
                  {actionItems.map((item) => (
                    <ActionItem key={item.account_id} item={item} />
                  ))}
                </ul>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No high-priority actions right now.</p>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
