import type { DashboardPerformance } from '@verdin/api-client';
import { Card } from '@verdin/ui';

interface BusinessMetricsProps {
  performance: DashboardPerformance;
}

export function BusinessMetrics({ performance }: BusinessMetricsProps) {
  const metrics = [
    { label: 'Avg accounts per case', value: performance.average_accounts_per_case },
    { label: 'Avg documents per case', value: performance.average_documents_per_case },
    { label: 'Cases opened this week', value: performance.cases_opened_this_week },
    { label: 'Cases completed this month', value: performance.cases_completed_this_month },
    { label: 'Resolution rate', value: `${performance.resolution_rate}%` },
    { label: 'Processing throughput (today)', value: performance.processing_throughput },
  ];

  return (
    <section aria-label="Business metrics">
      <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-500">
        Business Metrics
      </h2>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        {metrics.map((metric) => (
          <Card key={metric.label} className="!p-4">
            <p className="text-xs text-gray-500">{metric.label}</p>
            <p className="mt-1 text-lg font-semibold text-gray-900">{metric.value}</p>
          </Card>
        ))}
      </div>
    </section>
  );
}
