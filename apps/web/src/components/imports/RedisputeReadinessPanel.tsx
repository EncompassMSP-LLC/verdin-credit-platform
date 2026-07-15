import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseRedisputeReadiness,
  type AccountRedisputeReadiness,
  type CaseRedisputeReadinessSummary,
  type RedisputeAction,
  type RedisputePriority,
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

function actionBadgeVariant(
  priority: RedisputePriority,
): 'default' | 'info' | 'warning' | 'danger' | 'success' {
  switch (priority) {
    case 'high':
      return 'danger';
    case 'medium':
      return 'warning';
    default:
      return 'default';
  }
}

function SummaryBadges({ summary }: { summary: CaseRedisputeReadinessSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="danger">{summary.high_priority} high priority</Badge>
      <Badge variant="warning">{summary.redispute} re-dispute</Badge>
      <Badge variant="danger">{summary.escalate_cfpb + summary.escalate_attorney} escalate</Badge>
      <Badge variant="info">{summary.prepare_initial} prepare</Badge>
      <Badge variant="default">{summary.wait} awaiting</Badge>
      <Badge variant="success">{summary.resolved} resolved</Badge>
    </div>
  );
}

function ReadinessRow({ entry }: { entry: AccountRedisputeReadiness }) {
  return (
    <li className="flex flex-wrap items-start justify-between gap-2 rounded-md border border-gray-200 px-4 py-2.5">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-gray-900">{entry.creditor_name}</p>
        <p className="mt-0.5 text-xs text-gray-600">{entry.reason}</p>
        <p className="mt-0.5 text-xs text-gray-400">
          Round {entry.dispute_round}
          {entry.latest_outcome ? ` · last outcome: ${entry.latest_outcome}` : ''}
        </p>
      </div>
      <Badge variant={actionBadgeVariant(entry.priority)}>{ACTION_LABELS[entry.action]}</Badge>
    </li>
  );
}

export function CaseRedisputeReadinessPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const readinessQuery = useQuery({
    queryKey: ['case-redispute-readiness', caseId],
    queryFn: () => getCaseRedisputeReadiness(caseId),
    retry: false,
  });

  const entries = readinessQuery.data?.accounts ?? [];
  const actionable = entries.filter((entry) => entry.priority === 'high');
  const rest = entries.filter((entry) => entry.priority !== 'high');

  return (
    <div id={id} className={className}>
      <Card title="Re-dispute & escalation readiness">
        <p className="text-sm text-gray-500">
          Advisory next-step signals built from the §611 clock and recorded responses. High-priority
          items surface first. Suggestions only — the platform never files a dispute or escalation
          automatically.
        </p>

        {readinessQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading readiness signals…</p>
        ) : null}

        {readinessQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {readinessQuery.error instanceof ApiClientError
              ? readinessQuery.error.message
              : 'Failed to load re-dispute readiness'}
          </p>
        ) : null}

        {readinessQuery.data ? (
          <div className="mt-4 space-y-4">
            <SummaryBadges summary={readinessQuery.data.summary} />

            {entries.length === 0 ? (
              <p className="text-sm text-gray-500">No credit accounts in this case yet.</p>
            ) : (
              <>
                {actionable.length > 0 ? (
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                      Recommended actions
                    </p>
                    <ul className="space-y-2">
                      {actionable.map((entry) => (
                        <ReadinessRow key={entry.account_id} entry={entry} />
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No high-priority re-dispute actions.</p>
                )}

                {rest.length > 0 ? (
                  <details className="rounded-md border border-gray-100 px-3 py-2">
                    <summary className="cursor-pointer text-xs font-medium text-gray-600">
                      {rest.length} other tradeline(s)
                    </summary>
                    <ul className="mt-2 space-y-2">
                      {rest.map((entry) => (
                        <ReadinessRow key={entry.account_id} entry={entry} />
                      ))}
                    </ul>
                  </details>
                ) : null}
              </>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
