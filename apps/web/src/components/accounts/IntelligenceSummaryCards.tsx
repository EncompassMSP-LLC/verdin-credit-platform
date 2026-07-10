import type { Account, AccountIntelligenceSummary } from '@verdin/api-client';
import {
  ACCOUNT_STATUS_LABELS,
  ACCOUNT_TYPE_LABELS,
  BUREAU_LABELS,
  type AccountBureau,
  type AccountStatus,
  type AccountType,
} from '@verdin/shared';
import { Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function formatCurrency(value: string) {
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

function formatBreakdownLabel(key: string, kind: 'bureau' | 'type' | 'status') {
  if (kind === 'bureau') {
    return BUREAU_LABELS[key as AccountBureau] ?? key;
  }
  if (kind === 'type') {
    return ACCOUNT_TYPE_LABELS[key as AccountType] ?? key;
  }
  return ACCOUNT_STATUS_LABELS[key as AccountStatus] ?? key;
}

function BreakdownList({
  title,
  items,
  kind,
}: {
  title: string;
  items: Record<string, number>;
  kind: 'bureau' | 'type' | 'status';
}) {
  const entries = Object.entries(items).sort(([, left], [, right]) => right - left);
  if (entries.length === 0) return null;

  return (
    <Card title={title}>
      <ul className="space-y-2">
        {entries.map(([key, count]) => (
          <li key={key} className="flex items-center justify-between text-sm">
            <span className="text-gray-700">{formatBreakdownLabel(key, kind)}</span>
            <span className="font-medium text-gray-900">{count}</span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

function AccountHighlightList({
  title,
  accounts,
  metricLabel,
  metricValue,
}: {
  title: string;
  accounts: Account[];
  metricLabel: string;
  metricValue: (account: Account) => string;
}) {
  if (accounts.length === 0) return null;

  return (
    <Card title={title}>
      <ul className="divide-y divide-gray-100">
        {accounts.map((account) => (
          <li key={account.id} className="flex items-center justify-between gap-3 py-3">
            <Link
              to={`/accounts/${account.id}`}
              className="font-medium text-brand-600 hover:underline"
            >
              {account.creditor_name}
            </Link>
            <span className="text-sm text-gray-600">
              {metricLabel}: {metricValue(account)}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

interface IntelligenceSummaryCardsProps {
  summary: AccountIntelligenceSummary;
}

export function IntelligenceSummaryCards({ summary }: IntelligenceSummaryCardsProps) {
  const stats = [
    { label: 'Total accounts', value: String(summary.total_accounts) },
    { label: 'Total balance', value: formatCurrency(summary.total_balance) },
    { label: 'Collection accounts', value: String(summary.collection_count) },
    { label: 'Charge-off accounts', value: String(summary.charge_off_count) },
    { label: 'Critical accounts', value: String(summary.critical_accounts) },
    { label: 'Dispute ready', value: String(summary.dispute_ready_count) },
    { label: 'Evidence needed', value: String(summary.evidence_needed_count) },
    { label: 'Total past due', value: formatCurrency(summary.total_past_due) },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4 xl:grid-cols-8">
        {stats.map((stat) => (
          <Card key={stat.label} className="!p-4">
            <p className="text-xs text-gray-500">{stat.label}</p>
            <p className="mt-1 text-lg font-semibold text-gray-900">{stat.value}</p>
          </Card>
        ))}
      </div>

      <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
        <span className="rounded-full bg-gray-100 px-3 py-1">
          Scoring model: {summary.scoring_model ?? 'heuristic'}
        </span>
        {summary.cross_bureau?.available ? (
          <span className="rounded-full bg-blue-50 px-3 py-1 text-blue-800">
            Cross-bureau: {summary.cross_bureau.dispute_ready_discrepancies} dispute-ready ·{' '}
            {summary.cross_bureau.actionable_discrepancies} actionable
          </span>
        ) : null}
      </div>

      {summary.cross_bureau?.available ? (
        <Card title="Cross-bureau intelligence">
          <dl className="grid grid-cols-2 gap-4 text-sm md:grid-cols-3">
            <div>
              <dt className="text-xs text-gray-500">Reports compared</dt>
              <dd className="font-medium text-gray-900">
                {summary.cross_bureau.reports_compared.join(', ')}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Investigation needed</dt>
              <dd className="font-medium text-gray-900">
                {summary.cross_bureau.investigation_needed}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-gray-500">Consistent tradelines</dt>
              <dd className="font-medium text-gray-900">
                {summary.cross_bureau.consistent_tradelines}
              </dd>
            </div>
          </dl>
        </Card>
      ) : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <BreakdownList
          title="Accounts by bureau"
          items={summary.accounts_by_bureau}
          kind="bureau"
        />
        <BreakdownList title="Accounts by type" items={summary.accounts_by_type} kind="type" />
        <BreakdownList
          title="Accounts by status"
          items={summary.accounts_by_status}
          kind="status"
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <AccountHighlightList
          title="Highest balance accounts"
          accounts={summary.highest_balance_accounts}
          metricLabel="Balance"
          metricValue={(account) => formatCurrency(account.balance ?? '0')}
        />
        <AccountHighlightList
          title="Highest risk accounts"
          accounts={summary.highest_risk_accounts}
          metricLabel="Risk"
          metricValue={(account) => String(account.risk_score ?? '—')}
        />
      </div>

      {summary.next_action_queue.length > 0 ? (
        <Card title="Next action queue">
          <ul className="divide-y divide-gray-100">
            {summary.next_action_queue.map((item) => (
              <li key={item.account_id} className="py-3">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <Link
                      to={`/accounts/${item.account_id}`}
                      className="font-medium text-brand-600 hover:underline"
                    >
                      {item.creditor_name}
                    </Link>
                    <p className="text-sm text-gray-500">{item.recommended_action}</p>
                  </div>
                  <div className="flex gap-4 text-sm text-gray-600">
                    <span>Risk: {item.risk_score ?? '—'}</span>
                    <span>Readiness: {item.readiness_score ?? '—'}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
    </div>
  );
}
