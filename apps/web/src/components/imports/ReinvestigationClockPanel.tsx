import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseReinvestigationClock,
  type AccountReinvestigationClock,
  type CaseReinvestigationClockSummary,
  type ReinvestigationClockState,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';

const STATE_LABELS: Record<ReinvestigationClockState, string> = {
  not_sent: 'Not sent',
  awaiting: 'Awaiting',
  due_soon: 'Due soon',
  overdue: 'Overdue',
  responded: 'Responded',
};

function stateBadgeVariant(
  state: ReinvestigationClockState,
): 'default' | 'info' | 'warning' | 'danger' | 'success' {
  switch (state) {
    case 'overdue':
      return 'danger';
    case 'due_soon':
      return 'warning';
    case 'awaiting':
      return 'info';
    case 'responded':
      return 'success';
    default:
      return 'default';
  }
}

function SummaryBadges({ summary }: { summary: CaseReinvestigationClockSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="danger">{summary.overdue} overdue</Badge>
      <Badge variant="warning">{summary.due_soon} due soon</Badge>
      <Badge variant="info">{summary.awaiting} awaiting</Badge>
      <Badge variant="success">{summary.responded} responded</Badge>
      <Badge variant="default">{summary.not_sent} not sent</Badge>
    </div>
  );
}

function ClockRow({ entry }: { entry: AccountReinvestigationClock }) {
  return (
    <li className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-gray-200 px-4 py-2.5">
      <div>
        <p className="text-sm font-medium text-gray-900">{entry.creditor_name}</p>
        <p className="mt-0.5 text-xs text-gray-500">
          {entry.deadline
            ? `Deadline ${new Date(entry.deadline).toLocaleDateString()}`
            : 'No dispute mailed'}
          {entry.days_remaining !== null && entry.state !== 'responded'
            ? entry.days_remaining < 0
              ? ` · ${Math.abs(entry.days_remaining)}d overdue`
              : ` · ${entry.days_remaining}d left`
            : ''}
          {entry.response_count > 0 ? ` · ${entry.response_count} response(s) recorded` : ''}
        </p>
      </div>
      <Badge variant={stateBadgeVariant(entry.state)}>{STATE_LABELS[entry.state]}</Badge>
    </li>
  );
}

export function CaseReinvestigationClockPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const clockQuery = useQuery({
    queryKey: ['case-reinvestigation-clock', caseId],
    queryFn: () => getCaseReinvestigationClock(caseId),
    retry: false,
  });

  const entries = clockQuery.data?.accounts ?? [];
  const actionable = entries.filter(
    (entry) => entry.state === 'overdue' || entry.state === 'due_soon',
  );
  const rest = entries.filter((entry) => entry.state !== 'overdue' && entry.state !== 'due_soon');

  return (
    <div id={id} className={className}>
      <Card title="Reinvestigation clock (FCRA §611)">
        <p className="text-sm text-gray-500">
          Tracks the 30-day reinvestigation window from the dispute mail date. Overdue and due-soon
          tradelines surface first. Staff-entered responses only — no live bureau polling.
        </p>

        {clockQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading reinvestigation clock…</p>
        ) : null}

        {clockQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {clockQuery.error instanceof ApiClientError
              ? clockQuery.error.message
              : 'Failed to load reinvestigation clock'}
          </p>
        ) : null}

        {clockQuery.data ? (
          <div className="mt-4 space-y-4">
            <SummaryBadges summary={clockQuery.data.summary} />

            {entries.length === 0 ? (
              <p className="text-sm text-gray-500">No credit accounts in this case yet.</p>
            ) : (
              <>
                {actionable.length > 0 ? (
                  <div>
                    <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                      Needs attention
                    </p>
                    <ul className="space-y-2">
                      {actionable.map((entry) => (
                        <ClockRow key={entry.account_id} entry={entry} />
                      ))}
                    </ul>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No overdue or due-soon reinvestigations.</p>
                )}

                {rest.length > 0 ? (
                  <details className="rounded-md border border-gray-100 px-3 py-2">
                    <summary className="cursor-pointer text-xs font-medium text-gray-600">
                      {rest.length} other tradeline(s)
                    </summary>
                    <ul className="mt-2 space-y-2">
                      {rest.map((entry) => (
                        <ClockRow key={entry.account_id} entry={entry} />
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
