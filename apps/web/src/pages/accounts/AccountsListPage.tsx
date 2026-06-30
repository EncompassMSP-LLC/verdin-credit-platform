import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { getAccountIntelligenceSummary, listAccounts } from '@verdin/api-client';
import { ACCOUNT_TYPE_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import { AccountFilters, type AccountFiltersValue } from '../../components/accounts/AccountFilters';
import {
  AccountStatusChip,
  BureauBadge,
  DisputeStatusChip,
  ScoreDisplay,
} from '../../components/accounts/AccountBadges';
import { IntelligenceSummaryCards } from '../../components/accounts/IntelligenceSummaryCards';

const defaultFilters: AccountFiltersValue = {
  search: '',
  bureau: '',
  account_type: '',
  account_status: '',
  payment_status: '',
  dispute_status: '',
  dispute_ready: false,
  sort_by: 'created_at',
  sort_order: 'desc',
};

function formatCurrency(value: string | null) {
  if (!value) return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

export function AccountsListPage() {
  const [filters, setFilters] = useState<AccountFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      bureau: filters.bureau || undefined,
      account_type: filters.account_type || undefined,
      account_status: filters.account_status || undefined,
      payment_status: filters.payment_status || undefined,
      dispute_status: filters.dispute_status || undefined,
      dispute_ready: filters.dispute_ready || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['accounts', queryParams],
    queryFn: () => listAccounts(queryParams),
  });

  const summaryQuery = useQuery({
    queryKey: ['accounts-intelligence'],
    queryFn: () => getAccountIntelligenceSummary(),
  });

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Accounts</h1>
          <p className="mt-1 text-gray-500">Credit tradeline intelligence across all cases.</p>
        </div>
        <Link to="/accounts/new">
          <Button>New account</Button>
        </Link>
      </div>

      {summaryQuery.isLoading ? (
        <Card className="mb-6">
          <p className="py-6 text-center text-sm text-gray-500">Loading intelligence summary...</p>
        </Card>
      ) : null}

      {summaryQuery.data ? (
        <div className="mb-6">
          <IntelligenceSummaryCards summary={summaryQuery.data} />
        </div>
      ) : null}

      <Card className="mb-6">
        <AccountFilters
          value={filters}
          onChange={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading accounts...</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load accounts'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {!isLoading && !isError && data?.items.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No accounts found.</p>
            <Link to="/accounts/new" className="mt-4 inline-block">
              <Button>Create your first account</Button>
            </Link>
          </div>
        </Card>
      ) : null}

      {data && data.items.length > 0 ? (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead>
                <tr className="text-left text-gray-500">
                  <th className="px-4 py-3 font-medium">Creditor</th>
                  <th className="px-4 py-3 font-medium">Bureau</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Dispute</th>
                  <th className="px-4 py-3 font-medium">Balance</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Readiness</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data.items.map((account) => (
                  <tr key={account.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <Link
                        to={`/accounts/${account.id}`}
                        className="font-medium text-brand-600 hover:underline"
                      >
                        {account.creditor_name}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <BureauBadge bureau={account.bureau} />
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {ACCOUNT_TYPE_LABELS[account.account_type]}
                    </td>
                    <td className="px-4 py-3">
                      <AccountStatusChip status={account.account_status} />
                    </td>
                    <td className="px-4 py-3">
                      <DisputeStatusChip status={account.dispute_status} />
                    </td>
                    <td className="px-4 py-3 text-gray-700">{formatCurrency(account.balance)}</td>
                    <td className="px-4 py-3">
                      <ScoreDisplay label="" score={account.risk_score} variant="risk" />
                    </td>
                    <td className="px-4 py-3">
                      <ScoreDisplay label="" score={account.readiness_score} variant="readiness" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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
