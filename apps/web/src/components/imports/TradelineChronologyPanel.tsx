import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseTradelineChronology,
  type TradelineChronologyEvent,
  type TradelineChronologyItem,
  type TradelineChronologySummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function severityVariant(
  severity: TradelineChronologyEvent['severity'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (severity === 'high') return 'danger';
  if (severity === 'medium') return 'warning';
  return 'info';
}

function formatWhen(value: string | null | undefined) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

function SummaryBadges({ summary }: { summary: TradelineChronologySummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.tradelines} tradelines</Badge>
      <Badge variant="warning">{summary.with_changes} with changes</Badge>
      <Badge variant="info">{summary.events} events</Badge>
      <Badge variant="default">{summary.reports_evaluated} reports</Badge>
    </div>
  );
}

function TradelineCard({ item }: { item: TradelineChronologyItem }) {
  const [expanded, setExpanded] = useState(item.event_count > 0);

  return (
    <div className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">
            {item.creditor_name ?? 'Unknown creditor'}
            {item.account_number_masked ? ` · ${item.account_number_masked}` : ''}
          </p>
          <p className="mt-1 text-xs capitalize text-gray-500">
            {item.bureau} · {item.snapshot_count} snapshots · {item.event_count} events
          </p>
        </div>
        <button
          type="button"
          className="text-xs text-brand-600 hover:underline"
          onClick={() => setExpanded((value) => !value)}
        >
          {expanded ? 'Hide timeline' : 'Show timeline'}
        </button>
      </div>

      {expanded ? (
        <div className="mt-4 space-y-4">
          <ol className="space-y-2 border-l border-gray-200 pl-4">
            {item.snapshots.map((snap) => (
              <li key={`${snap.document_id}-${snap.parsed_at}`} className="relative">
                <span className="absolute -left-[1.28rem] top-1.5 h-2 w-2 rounded-full bg-gray-400" />
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <p className="text-sm text-gray-800">
                    {snap.present
                      ? `${snap.account_status ?? snap.payment_status ?? 'Reported'}${
                          snap.balance != null ? ` · balance ${snap.balance}` : ''
                        }${
                          snap.past_due_amount != null ? ` · past due ${snap.past_due_amount}` : ''
                        }`
                      : 'Not present on this report'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {snap.as_of_date ?? formatWhen(snap.parsed_at)}
                  </p>
                </div>
                <Link
                  to={`/documents/${snap.document_id}`}
                  className="text-xs text-brand-600 hover:underline"
                >
                  Open report
                </Link>
              </li>
            ))}
          </ol>

          {item.events.length > 0 ? (
            <ul className="space-y-2">
              {item.events.map((event, index) => (
                <li
                  key={`${event.event_type}-${event.to_document_id}-${event.field ?? ''}-${index}`}
                  className="rounded-md bg-gray-50 px-3 py-2"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant={severityVariant(event.severity)}>{event.event_type}</Badge>
                    <span className="text-sm text-gray-800">{event.summary}</span>
                  </div>
                  <p className="mt-1 text-xs text-gray-500">
                    {formatWhen(event.from_parsed_at)} → {formatWhen(event.to_parsed_at)}
                  </p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500">No field changes across stored reports.</p>
          )}
        </div>
      ) : null}
    </div>
  );
}

export function CaseTradelineChronologyPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const [bureau, setBureau] = useState<string>('');
  const chronologyQuery = useQuery({
    queryKey: ['case-tradeline-chronology', caseId, bureau || null],
    queryFn: () => getCaseTradelineChronology(caseId, bureau ? { bureau } : {}),
    retry: false,
  });

  const bureauOptions = useMemo(() => {
    const fromData = chronologyQuery.data?.bureaus ?? [];
    if (bureau && !fromData.includes(bureau)) {
      return [bureau, ...fromData];
    }
    return fromData;
  }, [bureau, chronologyQuery.data?.bureaus]);

  return (
    <div id={id} className={className}>
      <Card title="Tradeline reporting chronology">
        <p className="text-sm text-gray-500">
          Multi-report timeline of matched tradelines. Highlights balance rebounds, status
          transitions, appearances, and disappearances across stored bureau reports.
        </p>

        <div className="mt-3">
          <label
            htmlFor={`chronology-bureau-${caseId}`}
            className="block text-sm font-medium text-gray-700"
          >
            Bureau filter
          </label>
          <select
            id={`chronology-bureau-${caseId}`}
            className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 sm:max-w-xs"
            value={bureau}
            onChange={(event) => setBureau(event.target.value)}
          >
            <option value="">All bureaus</option>
            {bureauOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        {chronologyQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading tradeline chronology…</p>
        ) : null}

        {chronologyQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {chronologyQuery.error instanceof ApiClientError && chronologyQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : chronologyQuery.error instanceof Error
                ? chronologyQuery.error.message
                : 'Failed to load tradeline chronology'}
          </p>
        ) : null}

        {chronologyQuery.data ? (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">
                Bureaus:{' '}
                {chronologyQuery.data.bureaus.length > 0
                  ? chronologyQuery.data.bureaus.join(', ')
                  : 'none'}
              </p>
              <SummaryBadges summary={chronologyQuery.data.summary} />
            </div>

            {chronologyQuery.data.tradelines.length === 0 ? (
              <p className="text-sm text-gray-500">No tradelines found in parsed reports.</p>
            ) : (
              <div className="space-y-3">
                {chronologyQuery.data.tradelines.map((item) => (
                  <TradelineCard key={`${item.bureau}-${item.match_key}`} item={item} />
                ))}
              </div>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
