import type { DashboardTimelineItem } from '@verdin/api-client';
import { Link } from 'react-router-dom';
import { Card } from '@verdin/ui';

interface TimelineFeedProps {
  items: DashboardTimelineItem[];
}

function formatTime(value: string) {
  return new Date(value).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function TimelineFeed({ items }: TimelineFeedProps) {
  return (
    <Card title="Timeline Feed">
      <p className="mb-4 text-sm text-gray-500">
        Recent activity across cases, documents, and tasks.
      </p>
      {items.length === 0 ? (
        <p className="text-sm text-gray-500">No recent activity.</p>
      ) : (
        <ul className="space-y-5">
          {items.map((item) => (
            <li key={item.id} className="flex gap-4">
              <div className="w-14 shrink-0 text-right text-sm font-semibold tabular-nums text-gray-500">
                {formatTime(item.occurred_at)}
              </div>
              <div className="relative min-w-0 flex-1 border-l border-gray-200 pl-4">
                <span className="absolute -left-1 top-1.5 h-2 w-2 rounded-full bg-brand-500" />
                <p className="font-medium text-gray-900">{item.title}</p>
                {item.file_name ? (
                  <p className="mt-0.5 text-sm text-gray-600">{item.file_name}</p>
                ) : item.description ? (
                  <p className="mt-0.5 text-sm text-gray-600">{item.description}</p>
                ) : null}
                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                  {item.case_number && item.case_id ? (
                    <Link to={`/cases/${item.case_id}`} className="text-brand-600 hover:underline">
                      Case {item.case_number}
                    </Link>
                  ) : null}
                  {item.document_id ? (
                    <Link
                      to={`/documents/${item.document_id}`}
                      className="text-brand-600 hover:underline"
                    >
                      View document
                    </Link>
                  ) : null}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
