import type { AccountIntelligenceSummary } from '@verdin/api-client';
import { Card } from '@verdin/ui';

function formatCurrency(value: string) {
  const num = Number(value);
  if (Number.isNaN(num)) return value;
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(num);
}

interface IntelligenceSummaryCardsProps {
  summary: AccountIntelligenceSummary;
}

export function IntelligenceSummaryCards({ summary }: IntelligenceSummaryCardsProps) {
  const stats = [
    { label: 'Total accounts', value: String(summary.total_accounts) },
    { label: 'Total balance', value: formatCurrency(summary.total_balance) },
    { label: 'Critical accounts', value: String(summary.critical_accounts) },
    { label: 'Dispute ready', value: String(summary.dispute_ready_count) },
    { label: 'Evidence needed', value: String(summary.evidence_needed_count) },
    { label: 'Total past due', value: formatCurrency(summary.total_past_due) },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {stats.map((stat) => (
          <Card key={stat.label} className="!p-4">
            <p className="text-xs text-gray-500">{stat.label}</p>
            <p className="mt-1 text-lg font-semibold text-gray-900">{stat.value}</p>
          </Card>
        ))}
      </div>

      {summary.next_action_queue.length > 0 ? (
        <Card title="Next action queue">
          <ul className="divide-y divide-gray-100">
            {summary.next_action_queue.map((item) => (
              <li key={item.account_id} className="py-3">
                <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{item.creditor_name}</p>
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
