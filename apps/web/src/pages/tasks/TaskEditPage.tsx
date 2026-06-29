import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getTask } from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { TaskFormPage } from './TaskFormPage';

export function TaskEditPage() {
  const { taskId } = useParams<{ taskId: string }>();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['task', taskId],
    queryFn: () => getTask(taskId!),
    enabled: Boolean(taskId),
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

  return (
    <TaskFormPage
      mode="edit"
      taskId={data.id}
      defaultValues={{
        title: data.title,
        description: data.description,
        status: data.status,
        priority: data.priority,
        due_date: data.due_date,
        case_id: data.case_id,
        account_id: data.account_id,
        document_id: data.document_id,
        assigned_user_id: data.assigned_user_id,
      }}
    />
  );
}
