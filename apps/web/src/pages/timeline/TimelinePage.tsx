import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { listTimelineEvents } from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';

export interface TimelineFiltersValue {
  case_id: string;
  account_id: string;
  document_id: string;
  event_type: string;
  event_category: string;
  performed_by: string;
  occurred_from: string;
  occurred_to: string;
}

const defaultFilters: TimelineFiltersValue = {
  case_id: '',
  account_id: '',
  document_id: '',
  event_type: '',
  event_category: '',
  performed_by: '',
  occurred_from: '',
  occurred_to: '',
};

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

export function TimelinePage() {
  const [filters, setFilters] = useState<TimelineFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 25,
      case_id: filters.case_id || undefined,
      account_id: filters.account_id || undefined,
      document_id: filters.document_id || undefined,
      event_type: filters.event_type || undefined,
      event_category: filters.event_category || undefined,
      performed_by: filters.performed_by || undefined,
      occurred_from: filters.occurred_from
        ? new Date(filters.occurred_from).toISOString()
        : undefined,
      occurred_to: filters.occurred_to ? new Date(filters.occurred_to).toISOString() : undefined,
      sort_by: 'occurred_at' as const,
      sort_order: 'desc' as const,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['timeline', queryParams],
    queryFn: () => listTimelineEvents(queryParams),
  });

  const update = (patch: Partial<TimelineFiltersValue>) => {
    setFilters((current) => ({ ...current, ...patch }));
    setPage(1);
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Timeline</h1>
        <p className="mt-1 text-gray-500">
          Immutable audit stream across cases, accounts, documents, and platform activity.
        </p>
      </div>

      <Card className="mb-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Case ID</label>
            <input
              className={inputClass}
              value={filters.case_id}
              onChange={(e) => update({ case_id: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Account ID</label>
            <input
              className={inputClass}
              value={filters.account_id}
              onChange={(e) => update({ account_id: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Document ID</label>
            <input
              className={inputClass}
              value={filters.document_id}
              onChange={(e) => update({ document_id: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Event type</label>
            <input
              className={inputClass}
              placeholder="e.g. OCR_COMPLETED"
              value={filters.event_type}
              onChange={(e) => update({ event_type: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">Category</label>
            <select
              className={inputClass}
              value={filters.event_category}
              onChange={(e) => update({ event_category: e.target.value })}
            >
              <option value="">All categories</option>
              <option value="case">Case</option>
              <option value="account">Account</option>
              <option value="document">Document</option>
              <option value="auth">Auth</option>
              <option value="task">Task</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">User ID</label>
            <input
              className={inputClass}
              value={filters.performed_by}
              onChange={(e) => update({ performed_by: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">From</label>
            <input
              type="datetime-local"
              className={inputClass}
              value={filters.occurred_from}
              onChange={(e) => update({ occurred_from: e.target.value })}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">To</label>
            <input
              type="datetime-local"
              className={inputClass}
              value={filters.occurred_to}
              onChange={(e) => update({ occurred_to: e.target.value })}
            />
          </div>
        </div>
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading timeline...</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load timeline'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {data && data.items.length === 0 ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">No timeline events found.</p>
        </Card>
      ) : null}

      {data && data.items.length > 0 ? (
        <Card>
          <ul className="divide-y divide-gray-100">
            {data.items.map((event) => (
              <li key={event.id} className="py-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-xs text-gray-500">{formatDateTime(event.occurred_at)}</p>
                    <p className="font-medium text-gray-900">{event.title}</p>
                    {event.description ? (
                      <p className="mt-1 text-sm text-gray-600">{event.description}</p>
                    ) : null}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="info">{event.event_type}</Badge>
                    <Badge variant="default">{event.event_category}</Badge>
                    <Badge variant="default">{event.source_module}</Badge>
                  </div>
                </div>
                {Object.keys(event.metadata).length > 0 ? (
                  <dl className="mt-3 grid grid-cols-1 gap-2 text-sm sm:grid-cols-2">
                    {Object.entries(event.metadata).map(([key, value]) => (
                      <div key={key}>
                        <dt className="text-gray-500">{key}</dt>
                        <dd className="break-all">{String(value)}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}
              </li>
            ))}
          </ul>
          {data.pages > 1 ? (
            <div className="mt-4 flex items-center justify-between border-t border-gray-100 pt-4">
              <p className="text-sm text-gray-500">
                Page {data.page} of {data.pages} ({data.total} total)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
