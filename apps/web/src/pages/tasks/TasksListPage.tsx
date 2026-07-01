import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { listTasks, type Task } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { TaskFilters, type TaskFiltersValue } from '../../components/tasks/TaskFilters';
import {
  TaskOverdueBadge,
  TaskPriorityBadge,
  TaskStatusChip,
} from '../../components/tasks/TaskBadges';

const defaultFilters: TaskFiltersValue = {
  search: '',
  status: '',
  priority: '',
  source_module: '',
  overdue: false,
  sort_by: 'created_at',
  sort_order: 'desc',
};

function formatDate(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleDateString();
}

function isOverdue(task: Task) {
  if (!task.due_date) return false;
  if (task.status === 'completed' || task.status === 'canceled') return false;
  return new Date(task.due_date) < new Date();
}

export function TasksListPage() {
  const [filters, setFilters] = useState<TaskFiltersValue>(defaultFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 20,
      search: filters.search || undefined,
      status: filters.status || undefined,
      priority: filters.priority || undefined,
      source_module: filters.source_module || undefined,
      overdue: filters.overdue || undefined,
      sort_by: filters.sort_by,
      sort_order: filters.sort_order,
    }),
    [filters, page],
  );

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['tasks', queryParams],
    queryFn: () => listTasks(queryParams),
  });

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
          <p className="mt-1 text-gray-500">
            Operational work queue across cases, accounts, and documents.
          </p>
        </div>
        <Link to="/tasks/new">
          <Button>New task</Button>
        </Link>
      </div>

      <Card className="mb-6">
        <TaskFilters
          value={filters}
          onChange={(next) => {
            setFilters(next);
            setPage(1);
          }}
        />
      </Card>

      {isLoading ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading tasks...</p>
        </Card>
      ) : null}

      {isError ? (
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load tasks'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      ) : null}

      {!isLoading && !isError && data?.items.length === 0 ? (
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">No tasks found.</p>
        </Card>
      ) : null}

      {!isLoading && !isError && data && data.items.length > 0 ? (
        <Card className="overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Task
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Priority
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">
                    Due
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {data.items.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <Link
                        to={`/tasks/${task.id}`}
                        className="font-medium text-brand-600 hover:underline"
                      >
                        {task.title}
                      </Link>
                      {task.description ? (
                        <p className="mt-1 line-clamp-1 text-sm text-gray-500">
                          {task.description}
                        </p>
                      ) : null}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <TaskStatusChip status={task.status} />
                        {isOverdue(task) ? <TaskOverdueBadge /> : null}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <TaskPriorityBadge priority={task.priority} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{formatDate(task.due_date)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {data.pages > 1 ? (
            <div className="flex items-center justify-between border-t border-gray-200 px-6 py-4">
              <p className="text-sm text-gray-500">
                Page {data.page} of {data.pages} ({data.total} tasks)
              </p>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page <= 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  disabled={page >= data.pages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          ) : null}
        </Card>
      ) : null}
    </div>
  );
}
