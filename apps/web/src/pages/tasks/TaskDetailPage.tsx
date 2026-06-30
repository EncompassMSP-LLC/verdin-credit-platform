import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { completeTask, deleteTask, getTask, reopenTask } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { TaskPriorityBadge, TaskStatusChip } from '../../components/tasks/TaskBadges';

function formatDateTime(value: string | null) {
  if (!value) return '—';
  return new Date(value).toLocaleString();
}

export function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [confirmDelete, setConfirmDelete] = useState(false);

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTask(taskId!),
    enabled: Boolean(taskId),
  });

  const completeMutation = useMutation({
    mutationFn: () => completeTask(taskId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const reopenMutation = useMutation({
    mutationFn: () => reopenTask(taskId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['task', taskId] });
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteTask(taskId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      navigate('/tasks');
    },
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading task...</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Failed to load task'}
            </p>
            <Button variant="secondary" className="mt-4" onClick={() => refetch()}>
              Retry
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  const canComplete = data.status !== 'completed' && data.status !== 'canceled';
  const canReopen = data.status === 'completed' || data.status === 'canceled';

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/tasks" className="text-sm text-brand-600 hover:underline">
            ← Back to tasks
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.title}</h1>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <TaskStatusChip status={data.status} />
            <TaskPriorityBadge priority={data.priority} />
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/tasks/${data.id}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          {canComplete ? (
            <Button onClick={() => completeMutation.mutate()} disabled={completeMutation.isPending}>
              Complete
            </Button>
          ) : null}
          {canReopen ? (
            <Button
              variant="secondary"
              onClick={() => reopenMutation.mutate()}
              disabled={reopenMutation.isPending}
            >
              Reopen
            </Button>
          ) : null}
          <Button variant="secondary" onClick={() => setConfirmDelete(true)}>
            Delete
          </Button>
        </div>
      </div>

      {confirmDelete ? (
        <Card className="mb-6 border-red-200 bg-red-50">
          <p className="text-sm text-red-800">Delete this task? This action cannot be undone.</p>
          <div className="mt-4 flex gap-2">
            <Button
              variant="secondary"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              Confirm delete
            </Button>
            <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
              Cancel
            </Button>
          </div>
        </Card>
      ) : null}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <h2 className="text-lg font-semibold text-gray-900">Details</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="font-medium text-gray-500">Description</dt>
              <dd className="mt-1 text-gray-900">{data.description || '—'}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Due date</dt>
              <dd className="mt-1 text-gray-900">{formatDateTime(data.due_date)}</dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Completed at</dt>
              <dd className="mt-1 text-gray-900">{formatDateTime(data.completed_at)}</dd>
            </div>
          </dl>
        </Card>

        <Card>
          <h2 className="text-lg font-semibold text-gray-900">Links</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="font-medium text-gray-500">Case</dt>
              <dd className="mt-1">
                {data.case_id ? (
                  <Link to={`/cases/${data.case_id}`} className="text-brand-600 hover:underline">
                    View case
                  </Link>
                ) : (
                  '—'
                )}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Account</dt>
              <dd className="mt-1">
                {data.account_id ? (
                  <Link
                    to={`/accounts/${data.account_id}`}
                    className="text-brand-600 hover:underline"
                  >
                    View account
                  </Link>
                ) : (
                  '—'
                )}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Document</dt>
              <dd className="mt-1">
                {data.document_id ? (
                  <Link
                    to={`/documents/${data.document_id}`}
                    className="text-brand-600 hover:underline"
                  >
                    View document
                  </Link>
                ) : (
                  '—'
                )}
              </dd>
            </div>
            <div>
              <dt className="font-medium text-gray-500">Source module</dt>
              <dd className="mt-1 text-gray-900">{data.source_module || '—'}</dd>
            </div>
          </dl>
        </Card>
      </div>
    </div>
  );
}
