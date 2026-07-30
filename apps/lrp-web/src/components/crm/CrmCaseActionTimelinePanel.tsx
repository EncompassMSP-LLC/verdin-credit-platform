'use client';

import { ApiClientError, listTimelineEvents, type TimelineEvent } from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';
import { useMemo, useState } from 'react';

import { useCrmAuth } from '@/lib/crm/auth';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function metaString(metadata: Record<string, unknown>, key: string): string | null {
  const value = metadata[key];
  return typeof value === 'string' && value.length > 0 ? value : null;
}

function EventRow({ event }: { event: TimelineEvent }) {
  const source = metaString(event.metadata, 'source_id');
  const documentId = event.document_id;
  return (
    <li className="border-t border-navy-900/10 py-3 first:border-t-0">
      <p className="text-xs text-slate-500">{formatDateTime(event.occurred_at)}</p>
      <p className="text-sm font-medium text-navy-900">{event.title}</p>
      {event.description ? (
        <p className="mt-1 text-sm text-slate-600">{event.description}</p>
      ) : null}
      <p className="mt-1 text-xs text-slate-500">
        {event.event_type}
        {source ? ` · ${source}` : ''}
        {documentId ? ` · doc ${documentId.slice(0, 8)}…` : ''}
      </p>
    </li>
  );
}

type Props = {
  caseId: string | undefined;
};

export function CrmCaseActionTimelinePanel({ caseId }: Props) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const [sourceId, setSourceId] = useState('');
  const [sortOrder, setSortOrder] = useState<'desc' | 'asc'>('desc');

  const queryParams = useMemo(
    () => ({
      case_id: caseId!,
      source_id: sourceId.trim() || undefined,
      page: 1,
      page_size: 25,
      sort_by: 'occurred_at' as const,
      sort_order: sortOrder,
    }),
    [caseId, sourceId, sortOrder],
  );

  const query = useQuery({
    queryKey: ['crm', 'case-action-timeline', queryParams],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(caseId),
    queryFn: () => listTimelineEvents(queryParams),
    retry: false,
  });

  if (!caseId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Activity</h2>
        <p className="mt-2 text-sm text-slate-500">Link a case to view the action timeline.</p>
      </div>
    );
  }

  if (authMode !== 'platform') {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Activity</h2>
        <p className="mt-2 text-sm text-slate-500">
          Case timeline requires platform authentication (demo mode unavailable).
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-navy-900/10 bg-white p-4">
      <h2 className="text-sm font-semibold">Activity</h2>
      <p className="mt-2 text-sm text-slate-500">
        Append-only case action timeline — evidence links and related staff activity.
      </p>

      <div className="mt-3 flex flex-wrap items-end gap-2">
        <label className="block text-xs text-slate-600">
          Issue source_id
          <input
            className="mt-1 block w-full min-w-[14rem] rounded border border-navy-900/20 px-2 py-1 text-xs"
            value={sourceId}
            placeholder="Optional"
            onChange={(event) => setSourceId(event.target.value)}
          />
        </label>
        <button
          type="button"
          className={`rounded border px-2 py-1 text-xs ${
            sortOrder === 'desc'
              ? 'border-navy-900 bg-navy-900 text-white'
              : 'border-navy-900/20 bg-white text-navy-900'
          }`}
          onClick={() => setSortOrder('desc')}
        >
          Newest
        </button>
        <button
          type="button"
          className={`rounded border px-2 py-1 text-xs ${
            sortOrder === 'asc'
              ? 'border-navy-900 bg-navy-900 text-white'
              : 'border-navy-900/20 bg-white text-navy-900'
          }`}
          onClick={() => setSortOrder('asc')}
        >
          Oldest
        </button>
      </div>

      {query.isLoading ? <p className="mt-3 text-sm text-slate-500">Loading activity…</p> : null}

      {query.isError ? (
        <p className="mt-3 text-sm text-red-700">
          {query.error instanceof ApiClientError
            ? query.error.message
            : query.error instanceof Error
              ? query.error.message
              : 'Failed to load timeline'}
        </p>
      ) : null}

      {query.data && query.data.items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No timeline events yet.</p>
      ) : null}

      {query.data && query.data.items.length > 0 ? (
        <ul className="mt-2">
          {query.data.items.map((event) => (
            <EventRow key={event.id} event={event} />
          ))}
        </ul>
      ) : null}
    </div>
  );
}
