import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { createTask, updateTask } from '@verdin/api-client';
import {
  TASK_PRIORITIES,
  TASK_PRIORITY_LABELS,
  TASK_STATUSES,
  TASK_STATUS_LABELS,
} from '@verdin/shared';
import { createTaskSchema, type CreateTaskInput, type UpdateTaskInput } from '@verdin/validation';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface TaskFormPageProps {
  mode: 'create' | 'edit';
  taskId?: string;
  defaultValues?: CreateTaskInput;
}

export function TaskFormPage({ mode, taskId, defaultValues }: TaskFormPageProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateTaskInput>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: defaultValues ?? {
      title: '',
      description: '',
      status: 'open',
      priority: 'medium',
      due_date: null,
      case_id: null,
      account_id: null,
      document_id: null,
      assigned_user_id: null,
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: CreateTaskInput) => {
      const payload = {
        ...values,
        description: values.description || null,
        due_date: values.due_date || null,
        case_id: values.case_id || null,
        account_id: values.account_id || null,
        document_id: values.document_id || null,
        assigned_user_id: values.assigned_user_id || null,
      };
      if (mode === 'create') {
        return createTask(payload);
      }
      if (!taskId) throw new Error('Task ID is required');
      return updateTask(taskId, payload as UpdateTaskInput);
    },
    onSuccess: (task) => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      queryClient.invalidateQueries({ queryKey: ['task', task.id] });
      navigate(`/tasks/${task.id}`);
    },
    onError: (err) => {
      setError(err instanceof Error ? err.message : 'Failed to save task');
    },
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          to={mode === 'edit' && taskId ? `/tasks/${taskId}` : '/tasks'}
          className="text-sm text-brand-600 hover:underline"
        >
          ← Back
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">
          {mode === 'create' ? 'New task' : 'Edit task'}
        </h1>
      </div>

      <Card className="max-w-2xl">
        <form
          className="space-y-6"
          onSubmit={handleSubmit((values) => {
            setError(null);
            mutation.mutate(values);
          })}
        >
          <div>
            <label className="block text-sm font-medium text-gray-700" htmlFor="title">
              Title
            </label>
            <input id="title" className={inputClass} {...register('title')} />
            {errors.title ? (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            ) : null}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700" htmlFor="description">
              Description
            </label>
            <textarea
              id="description"
              rows={4}
              className={inputClass}
              {...register('description')}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="status">
                Status
              </label>
              <select id="status" className={inputClass} {...register('status')}>
                {TASK_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {TASK_STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="priority">
                Priority
              </label>
              <select id="priority" className={inputClass} {...register('priority')}>
                {TASK_PRIORITIES.map((priority) => (
                  <option key={priority} value={priority}>
                    {TASK_PRIORITY_LABELS[priority]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700" htmlFor="due_date">
              Due date
            </label>
            <input
              id="due_date"
              type="datetime-local"
              className={inputClass}
              {...register('due_date')}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="case_id">
                Case ID
              </label>
              <input
                id="case_id"
                className={inputClass}
                placeholder="Optional UUID"
                {...register('case_id')}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700" htmlFor="assigned_user_id">
                Assigned user ID
              </label>
              <input
                id="assigned_user_id"
                className={inputClass}
                placeholder="Optional UUID"
                {...register('assigned_user_id')}
              />
            </div>
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          <div className="flex gap-3">
            <Button type="submit" disabled={isSubmitting || mutation.isPending}>
              {mode === 'create' ? 'Create task' : 'Save changes'}
            </Button>
            <Link to={mode === 'edit' && taskId ? `/tasks/${taskId}` : '/tasks'}>
              <Button type="button" variant="secondary">
                Cancel
              </Button>
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
}
