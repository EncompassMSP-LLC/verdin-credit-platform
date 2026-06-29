import type { DashboardKpis } from '@verdin/api-client';
import { Card } from '@verdin/ui';

interface KpiRowProps {
  kpis: DashboardKpis;
}

const KPI_CONFIG = [
  { key: 'open_cases' as const, label: 'Open Cases', color: 'text-blue-600' },
  { key: 'active_accounts' as const, label: 'Active Accounts', color: 'text-emerald-600' },
  { key: 'pending_tasks' as const, label: 'Pending Tasks', color: 'text-amber-600' },
  { key: 'documents_processing' as const, label: 'Documents Processing', color: 'text-violet-600' },
  { key: 'ocr_queue' as const, label: 'OCR Queue', color: 'text-orange-600' },
  {
    key: 'average_resolution_time_hours' as const,
    label: 'Avg Resolution Time',
    color: 'text-slate-700',
    format: (value: number | null) => (value != null ? `${value}h` : '—'),
  },
];

export function KpiRow({ kpis }: KpiRowProps) {
  return (
    <section aria-label="Executive KPIs">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Executive KPIs
      </h2>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
        {KPI_CONFIG.map((item) => {
          const raw = kpis[item.key];
          const value =
            'format' in item && item.format
              ? item.format(raw as number | null)
              : String(raw ?? '—');

          return (
            <Card key={item.key} className="!p-4">
              <p className="text-xs text-gray-500">{item.label}</p>
              <p className={`mt-1 text-2xl font-bold ${item.color}`}>{value}</p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
