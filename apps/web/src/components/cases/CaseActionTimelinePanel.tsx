import { useQuery } from '@tanstack/react-query';
import { ApiClientError, listTimelineEvents, type TimelineEvent } from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function metaString(metadata: Record<string, unknown>, key: string): string | null {
  const value = metadata[key];
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function EventLinks({ event }: { event: TimelineEvent }) {
  const sourceId = metaString(event.metadata, 'source_id');
  const disputeLetterId = metaString(event.metadata, 'dispute_letter_id');
  const links: { label: string; to: string }[] = [];

  if (event.document_id) {
    links.push({ label: 'Document', to: `/documents/${event.document_id}` });
  }
  if (event.case_id && sourceId) {
    links.push({
      label: 'Issue cards',
      to: `/cases/${event.case_id}#issue-explainability`,
    });
  }
  if (event.case_id && (disputeLetterId || event.event_type.includes('LETTER'))) {
    links.push({
      label: 'Letter drafts',
      to: `/cases/${event.case_id}#letter-draft-builder`,
    });
  }

  if (links.length === 0) return null;

  return (
    <div className="mt-2 flex flex-wrap gap-3 text-xs">
      {links.map((link) => (
        <Link key={link.to + link.label} to={link.to} className="text-brand-700 hover:underline">
          {link.label}
        </Link>
      ))}
    </div>
  );
}

export function CaseActionTimelinePanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const [sourceId, setSourceId] = useState('');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      case_id: caseId,
      source_id: sourceId.trim() || undefined,
      page,
      page_size: 20,
      sort_by: 'occurred_at' as const,
      sort_order: sortOrder,
    }),
    [caseId, sourceId, page, sortOrder],
  );

  const query = useQuery({
    queryKey: ['case-action-timeline', queryParams],
    queryFn: () => listTimelineEvents(queryParams),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Case action timeline">
        <p className="text-sm text-gray-500">
          Append-only staff audit stream for this case — evidence links, documents, letters, and
          related platform activity. Filter by issue <code>source_id</code> when present.
        </p>

        <div className="mt-3 flex flex-wrap items-end gap-3">
          <label className="block text-xs text-gray-600">
            Issue source_id
            <input
              className="mt-1 block w-72 rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              value={sourceId}
              placeholder="Optional issue filter"
              onChange={(event) => {
                setSourceId(event.target.value);
                setPage(1);
              }}
            />
          </label>
          <div className="flex gap-2">
            <Button
              type="button"
              size="sm"
              variant={sortOrder === 'desc' ? 'primary' : 'secondary'}
              onClick={() => {
                setSortOrder('desc');
                setPage(1);
              }}
            >
              Newest first
            </Button>
            <Button
              type="button"
              size="sm"
              variant={sortOrder === 'asc' ? 'primary' : 'secondary'}
              onClick={() => {
                setSortOrder('asc');
                setPage(1);
              }}
            >
              Oldest first
            </Button>
          </div>
        </div>

        {query.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading case timeline…</p>
        ) : null}

        {query.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {query.error instanceof ApiClientError
              ? query.error.message
              : query.error instanceof Error
                ? query.error.message
                : 'Failed to load timeline'}
          </p>
        ) : null}

        {query.data && query.data.items.length === 0 ? (
          <p className="mt-3 text-sm text-gray-500">No timeline events for this case yet.</p>
        ) : null}

        {query.data && query.data.items.length > 0 ? (
          <ul className="mt-3 divide-y divide-gray-100">
            {query.data.items.map((event) => {
              const source = metaString(event.metadata, 'source_id');
              const actorType = metaString(event.metadata, 'actor_type');
              return (
                <li key={event.id} className="py-3">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <p className="text-xs text-gray-500">{formatDateTime(event.occurred_at)}</p>
                      <p className="text-sm font-medium text-gray-900">{event.title}</p>
                      {event.description ? (
                        <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                      ) : null}
                      <EventLinks event={event} />
                    </div>
                    <div className="flex flex-wrap gap-1">
                      <Badge variant="info">{event.event_type}</Badge>
                      <Badge variant="default">{event.event_category}</Badge>
                      {source ? <Badge variant="default">issue</Badge> : null}
                      {actorType ? <Badge variant="default">{actorType}</Badge> : null}
                    </div>
                  </div>
                  {source ? <p className="mt-1 font-mono text-xs text-gray-500">{source}</p> : null}
                </li>
              );
            })}
          </ul>
        ) : null}

        {query.data && query.data.pages > 1 ? (
          <div className="mt-3 flex items-center justify-between text-sm text-gray-600">
            <Button
              type="button"
              size="sm"
              variant="secondary"
              disabled={page <= 1}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
            >
              Previous
            </Button>
            <span>
              Page {query.data.page} of {query.data.pages}
            </span>
            <Button
              type="button"
              size="sm"
              variant="secondary"
              disabled={page >= query.data.pages}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </Button>
          </div>
        ) : null}
      </Card>
    </div>
  );
}
