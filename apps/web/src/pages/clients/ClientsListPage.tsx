import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listClients } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { ClientFilters, type ClientFiltersValue } from '../../components/clients/ClientFilters';
import { ClientStatusBadge } from '../../components/clients/ClientStatusBadge';

const defaultFilters: ClientFiltersValue = {
  search: '',
  status: '',
  sort_by: 'created_at',
  sort_order: 'desc',
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

export function ClientsListPage() {
  const [filters, setFilters] = useState<ClientFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      status: filters.status || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['clients', queryParams],
    queryFn: () => listClients(queryParams),
  });

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clients</h1>
          <p className="mt-1 text-gray-500">Manage client profiles, contacts, and portal access.</p>
        </div>
        <Link to="/clients/new">
          <Button>New client</Button>
        </Link>
      </div>

      <Card className="mb-6">
        <ClientFilters
          value={filters}
          onChange={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading clients…</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load clients'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {data ? (
        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Updated
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {data.items.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-12 text-center text-sm text-gray-500">
                      No clients found.
                    </td>
                  </tr>
                ) : (
                  data.items.map((client) => (
                    <tr key={client.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <Link
                          to={`/clients/${client.id}`}
                          className="font-medium text-brand-700 hover:underline"
                        >
                          {client.display_name}
                        </Link>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{client.email ?? '—'}</td>
                      <td className="px-6 py-4">
                        <ClientStatusBadge status={client.status} />
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {formatDate(client.updated_at)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {data.pages > 1 ? (
            <div className="flex items-center justify-between border-t border-gray-200 px-6 py-4">
              <p className="text-sm text-gray-500">
                Page {data.page} of {data.pages} ({data.total} clients)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  disabled={page <= 1}
                  onClick={() => setPage((current) => Math.max(1, current - 1))}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  disabled={page >= data.pages}
                  onClick={() => setPage((current) => current + 1)}
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
