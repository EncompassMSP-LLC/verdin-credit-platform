import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listCases, type Case } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { CASE_STAGE_LABELS } from '@verdin/shared';
import { CaseFilters, type CaseFiltersValue } from '../../components/cases/CaseFilters';
import { CasePriorityBadge, CaseStatusChip } from '../../components/cases/CaseBadges';

const defaultFilters: CaseFiltersValue = {
  search: '',
  status: '',
  stage: '',
  priority: '',
  sort_by: 'created_at',
  sort_order: 'desc',
};

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

export function CasesListPage() {
  const [filters, setFilters] = useState<CaseFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      status: filters.status || undefined,
      stage: filters.stage || undefined,
      priority: filters.priority || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['cases', queryParams],
    queryFn: () => listCases(queryParams),
  });

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cases</h1>
          <p className="mt-1 text-gray-500">Manage credit review cases.</p>
        </div>
        <Link to="/cases/new">
          <Button>New case</Button>
        </Link>
      </div>

      <Card className="mb-6">
        <CaseFilters
          value={filters}
          onChange={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading cases...</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load cases'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {!isLoading && !isError && data && data.items.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <h3 className="text-base font-semibold text-gray-900">No cases found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Create a case or adjust your filters to see results.
            </p>
            <Link to="/cases/new" className="mt-4 inline-block">
              <Button>Create case</Button>
            </Link>
          </div>
        </Card>
      ) : null}

      {!isLoading && !isError && data && data.items.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-gray-200 bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Case</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Client</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Status</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Stage</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Priority</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-500">Opened</th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((item: Case) => (
                  <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/cases/${item.id}`}
                        className="font-medium text-brand-600 hover:underline"
                      >
                        {item.title}
                      </Link>
                      {item.case_number ? (
                        <p className="text-xs text-gray-500">{item.case_number}</p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3">
                      <p>{item.client_name}</p>
                      {item.client_email ? (
                        <p className="text-xs text-gray-500">{item.client_email}</p>
                      ) : null}
                    </td>
                    <td className="px-4 py-3">
                      <CaseStatusChip status={item.status} />
                    </td>
                    <td className="px-4 py-3 text-gray-700">{CASE_STAGE_LABELS[item.stage]}</td>
                    <td className="px-4 py-3">
                      <CasePriorityBadge priority={item.priority} />
                    </td>
                    <td className="px-4 py-3 text-gray-700">{formatDate(item.opened_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex items-center justify-between border-t border-gray-200 px-4 py-3">
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
        </Card>
      ) : null}
    </div>
  );
}
