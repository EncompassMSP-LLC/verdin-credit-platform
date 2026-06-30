import { Card } from '@verdin/ui';

interface DashboardMetricCardProps {
  label: string;
  value: string | number;
  tone?: 'default' | 'info' | 'success' | 'warning' | 'danger';
}

const toneClasses: Record<NonNullable<DashboardMetricCardProps['tone']>, string> = {
  default: 'text-gray-900',
  info: 'text-blue-600',
  success: 'text-emerald-600',
  warning: 'text-amber-600',
  danger: 'text-red-600',
};

export function DashboardMetricCard({ label, value, tone = 'default' }: DashboardMetricCardProps) {
  return (
    <Card className="!p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className={`mt-2 text-2xl font-bold tabular-nums ${toneClasses[tone]}`}>{value}</p>
    </Card>
  );
}
