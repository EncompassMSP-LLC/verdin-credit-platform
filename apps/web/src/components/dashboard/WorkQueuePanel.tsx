import type { DashboardQueueItem } from '@verdin/api-client';
import { Link } from 'react-router-dom';
import { Card } from '@verdin/ui';

interface WorkQueuePanelProps {
  title: string;
  items: DashboardQueueItem[];
  emptyMessage: string;
}

function queueItemLink(item: DashboardQueueItem): string {
  if (item.entity_type === 'task') return `/tasks/${item.id}`;
  if (item.entity_type === 'case') return `/cases/${item.id}`;
  return `/documents/${item.id}`;
}

function formatDueDate(value: string | null) {
  if (!value) return null;
  return new Date(value).toLocaleDateString();
}

export function WorkQueuePanel({ title, items, emptyMessage }: WorkQueuePanelProps) {
  return (
    <Card title={title}>
      {items.length === 0 ? (
        <p className="text-sm text-gray-500">{emptyMessage}</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {items.map((item) => (
            <li key={`${item.entity_type}-${item.id}`} className="py-3 first:pt-0 last:pb-0">
              <Link
                to={queueItemLink(item)}
                className="group block rounded-md transition hover:bg-gray-50 -mx-2 px-2 py-1"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <p className="truncate font-medium text-gray-900 group-hover:text-brand-700">
                      {item.title}
                    </p>
                    {item.subtitle ? (
                      <p className="truncate text-sm text-gray-500">{item.subtitle}</p>
                    ) : null}
                    {item.case_number ? (
                      <p className="mt-0.5 text-xs text-gray-400">Case #{item.case_number}</p>
                    ) : null}
                  </div>
                  <div className="shrink-0 text-right text-xs text-gray-500">
                    {item.priority ? (
                      <span className="mb-1 block uppercase">{item.priority}</span>
                    ) : null}
                    {item.due_date ? <span>Due {formatDueDate(item.due_date)}</span> : null}
                  </div>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
