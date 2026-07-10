import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listCases, listClientAccounts } from '@verdin/api-client';
import { ACCOUNT_TYPE_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import {
  AccountStatusChip,
  BureauBadge,
  DisputeStatusChip,
  ScoreDisplay,
} from '../accounts/AccountBadges';

function formatCurrency(value: string | null) {
  if (!value) return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

interface ClientAccountsPanelProps {
  clientId: string;
}

export function ClientAccountsPanel({ clientId }: ClientAccountsPanelProps) {
  const accountsQuery = useQuery({
    queryKey: ['client-accounts', clientId],
    queryFn: () =>
      listClientAccounts(clientId, { page_size: 50, sort_by: 'risk_score', sort_order: 'desc' }),
    enabled: Boolean(clientId),
  });

  const casesQuery = useQuery({
    queryKey: ['client-cases', clientId],
    queryFn: () => listCases({ client_id: clientId, page_size: 50 }),
    enabled: Boolean(clientId),
  });

  const caseTitles = new Map(
    (casesQuery.data?.items ?? []).map((caseItem) => [caseItem.id, caseItem.title]),
  );

  return (
    <Card className="mt-8 p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Accounts</h2>
          <p className="mt-1 text-sm text-gray-600">
            Tradelines across all cases linked to this client.
          </p>
        </div>
        <Link to={`/cases/new?client_id=${clientId}`}>
          <Button variant="secondary">New case</Button>
        </Link>
      </div>

      {accountsQuery.isLoading ? (
        <p className="mt-6 py-8 text-center text-sm text-gray-500">Loading accounts...</p>
      ) : null}

      {accountsQuery.isError ? (
        <p className="mt-6 py-8 text-center text-sm text-red-600">Failed to load client accounts</p>
      ) : null}

      {accountsQuery.data?.items.length === 0 ? (
        <p className="mt-6 text-sm text-gray-500">
          No accounts yet. Add tradelines from a linked case.
        </p>
      ) : null}

      {accountsQuery.data && accountsQuery.data.items.length > 0 ? (
        <div className="mt-6 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-4 py-3 font-medium">Creditor</th>
                <th className="px-4 py-3 font-medium">Case</th>
                <th className="px-4 py-3 font-medium">Bureau</th>
                <th className="px-4 py-3 font-medium">Type</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Dispute</th>
                <th className="px-4 py-3 font-medium">Balance</th>
                <th className="px-4 py-3 font-medium">Scores</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {accountsQuery.data.items.map((account) => (
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
                    <Link
                      to={`/cases/${account.case_id}/accounts`}
                      className="text-brand-600 hover:underline"
                    >
                      {caseTitles.get(account.case_id) ?? 'View case accounts'}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <BureauBadge bureau={account.bureau} />
                  </td>
                  <td className="px-4 py-3">{ACCOUNT_TYPE_LABELS[account.account_type]}</td>
                  <td className="px-4 py-3">
                    <AccountStatusChip status={account.account_status} />
                  </td>
                  <td className="px-4 py-3">
                    <DisputeStatusChip status={account.dispute_status} />
                  </td>
                  <td className="px-4 py-3">{formatCurrency(account.balance)}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-3">
                      <ScoreDisplay label="Risk" score={account.risk_score} variant="risk" />
                      <ScoreDisplay
                        label="Ready"
                        score={account.readiness_score}
                        variant="readiness"
                      />
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </Card>
  );
}
