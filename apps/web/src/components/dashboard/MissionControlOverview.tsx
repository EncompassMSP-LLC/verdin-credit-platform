import type { DashboardOverview } from '@verdin/api-client';
import { DashboardMetricCard } from './DashboardMetricCard';

interface MissionControlOverviewProps {
  overview: DashboardOverview;
}

export function MissionControlOverview({ overview }: MissionControlOverviewProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 xl:grid-cols-6">
      <DashboardMetricCard label="Open Cases" value={overview.open_cases} tone="info" />
      <DashboardMetricCard
        label="Active Accounts"
        value={overview.active_accounts}
        tone="success"
      />
      <DashboardMetricCard label="Documents" value={overview.documents} />
      <DashboardMetricCard
        label="Tasks Due Today"
        value={overview.tasks_due_today}
        tone="warning"
      />
      <DashboardMetricCard label="Overdue Tasks" value={overview.overdue_tasks} tone="danger" />
      <DashboardMetricCard label="Active Alerts" value={overview.alert_count} tone="danger" />
    </div>
  );
}
