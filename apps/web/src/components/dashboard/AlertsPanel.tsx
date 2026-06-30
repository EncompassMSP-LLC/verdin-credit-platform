import type { DashboardAlertItem } from '@verdin/api-client';
import { Link } from 'react-router-dom';
import { Card } from '@verdin/ui';

interface AlertsPanelProps {
  alerts: DashboardAlertItem[];
  total: number;
}

function alertLink(alert: DashboardAlertItem): string {
  if (alert.entity_type === 'task') return `/tasks/${alert.entity_id}`;
  if (alert.entity_type === 'case') return `/cases/${alert.entity_id}`;
  return `/documents/${alert.entity_id}`;
}

const severityClasses: Record<DashboardAlertItem['severity'], string> = {
  critical: 'border-red-300 bg-red-50 text-red-800',
  high: 'border-orange-300 bg-orange-50 text-orange-800',
  medium: 'border-amber-300 bg-amber-50 text-amber-800',
};

const alertTypeLabels: Record<DashboardAlertItem['alert_type'], string> = {
  ocr_failure: 'OCR Failure',
  unmatched_entity: 'Unmatched Entity',
  document_review: 'Review Required',
  overdue_task: 'Overdue Task',
};

export function AlertsPanel({ alerts, total }: AlertsPanelProps) {
  return (
    <Card title="Alerts">
      <p className="mb-4 text-sm text-gray-500">
        Operational issues requiring attention ({total}).
      </p>
      {alerts.length === 0 ? (
        <p className="text-sm text-gray-500">No active alerts. Operations are healthy.</p>
      ) : (
        <ul className="space-y-3">
          {alerts.map((alert) => (
            <li key={alert.id}>
              <Link
                to={alertLink(alert)}
                className={`block rounded-lg border px-3 py-3 transition hover:opacity-90 ${severityClasses[alert.severity]}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-xs font-semibold uppercase tracking-wide opacity-80">
                      {alertTypeLabels[alert.alert_type]}
                    </p>
                    <p className="mt-1 font-medium">{alert.title}</p>
                    <p className="mt-0.5 truncate text-sm opacity-80">{alert.message}</p>
                  </div>
                  <span className="shrink-0 text-xs font-medium uppercase">{alert.severity}</span>
                </div>
                {alert.case_number ? (
                  <p className="mt-2 text-xs opacity-70">Case #{alert.case_number}</p>
                ) : null}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
