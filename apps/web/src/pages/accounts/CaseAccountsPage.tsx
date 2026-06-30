import { useQuery } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import { getAccountIntelligenceSummary, getCase, listCaseAccounts } from '@verdin/api-client';
import { ACCOUNT_TYPE_LABELS } from '@verdin/shared';
import { Button, Card } from '@verdin/ui';
import {
  AccountStatusChip,
  BureauBadge,
  DisputeStatusChip,
  ScoreDisplay,
} from '../../components/accounts/AccountBadges';
import { IntelligenceSummaryCards } from '../../components/accounts/IntelligenceSummaryCards';

function formatCurrency(value: string | null) {
  if (!value) return '—';
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

export function CaseAccountsPage() {
  const { caseId } = useParams<{ caseId: string }>();

  const caseQuery = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: Boolean(caseId),
  });

  const accountsQuery = useQuery({
    queryKey: ['case-accounts', caseId],
    queryFn: () => listCaseAccounts(caseId!),
    enabled: Boolean(caseId),
  });

  const summaryQuery = useQuery({
    queryKey: ['accounts-intelligence', caseId],
    queryFn: () => getAccountIntelligenceSummary(caseId),
    enabled: Boolean(caseId),
  });

  if (!caseId) return null;

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to={`/cases/${caseId}`} className="text-sm text-brand-600 hover:underline">
            ← Back to case
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">
            Case accounts
            {caseQuery.data ? `: ${caseQuery.data.title}` : ''}
          </h1>
        </div>
        <Link to={`/accounts/new?case_id=${caseId}`}>
          <Button>Add account</Button>
        </Link>
      </div>

      {summaryQuery.data ? (
        <div className="mb-6">
          <IntelligenceSummaryCards summary={summaryQuery.data} />
        </div>
      ) : null}

      {accountsQuery.isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading accounts...</p>
        </Card>
      ) : null}

      {accountsQuery.isError ? (
        <Card>
          <p className="py-8 text-center text-sm text-red-600">Failed to load case accounts</p>
        </Card>
      ) : null}

      {accountsQuery.data?.items.length === 0 ? (
        <Card>
          <div className="py-12 text-center">
            <p className="text-sm text-gray-500">No accounts linked to this case yet.</p>
            <Link to={`/accounts/new?case_id=${caseId}`} className="mt-4 inline-block">
              <Button>Add account</Button>
            </Link>
          </div>
        </Card>
      ) : null}

      {accountsQuery.data && accountsQuery.data.items.length > 0 ? (
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
        </Card>
      ) : null}
    </div>
  );
}
