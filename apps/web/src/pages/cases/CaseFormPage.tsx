import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { createCase, updateCase } from '@verdin/api-client';
import { createCaseSchema, type CreateCaseInput, type UpdateCaseInput } from '@verdin/validation';
import {
  CASE_PRIORITIES,
  CASE_PRIORITY_LABELS,
  CASE_STAGES,
  CASE_STAGE_LABELS,
  CASE_STATUSES,
  CASE_STATUS_LABELS,
} from '@verdin/shared';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface CaseFormPageProps {
  mode: 'create' | 'edit';
  caseId?: string;
  defaultValues?: CreateCaseInput;
}

export function CaseFormPage({ mode, caseId, defaultValues }: CaseFormPageProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateCaseInput>({
    resolver: zodResolver(createCaseSchema),
    defaultValues: defaultValues ?? {
      title: '',
      client_name: '',
      client_email: '',
      status: 'open',
      stage: 'intake',
      priority: 'medium',
      summary: '',
      notes: '',
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: CreateCaseInput) => {
      const payload = {
        ...values,
        client_email: values.client_email || null,
      };
      if (mode === 'create') {
        return createCase(payload);
      }
      if (!caseId) throw new Error('Case ID is required');
      return updateCase(caseId, payload as UpdateCaseInput);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['case', result.id] });
      navigate(`/cases/${result.id}`);
    },
    onError: (err: Error) => setError(err.message),
  });

  const onSubmit = handleSubmit((values) => {
    setError(null);
    mutation.mutate(values);
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <Link
          to={caseId ? `/cases/${caseId}` : '/cases'}
          className="text-sm text-brand-600 hover:underline"
        >
          ← Back
        </Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">
          {mode === 'create' ? 'Create case' : 'Edit case'}
        </h1>
      </div>

      <Card className="max-w-3xl">
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700">
              Title
            </label>
            <input id="title" className={inputClass} {...register('title')} />
            {errors.title ? (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            ) : null}
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">
                Client name
              </label>
              <input id="client_name" className={inputClass} {...register('client_name')} />
              {errors.client_name ? (
                <p className="mt-1 text-sm text-red-600">{errors.client_name.message}</p>
              ) : null}
            </div>
            <div>
              <label htmlFor="client_email" className="block text-sm font-medium text-gray-700">
                Client email
              </label>
              <input
                id="client_email"
                type="email"
                className={inputClass}
                {...register('client_email')}
              />
              {errors.client_email ? (
                <p className="mt-1 text-sm text-red-600">{errors.client_email.message}</p>
              ) : null}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700">
                Status
              </label>
              <select id="status" className={inputClass} {...register('status')}>
                {CASE_STATUSES.map((status) => (
                  <option key={status} value={status}>
                    {CASE_STATUS_LABELS[status]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="stage" className="block text-sm font-medium text-gray-700">
                Stage
              </label>
              <select id="stage" className={inputClass} {...register('stage')}>
                {CASE_STAGES.map((stage) => (
                  <option key={stage} value={stage}>
                    {CASE_STAGE_LABELS[stage]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                Priority
              </label>
              <select id="priority" className={inputClass} {...register('priority')}>
                {CASE_PRIORITIES.map((priority) => (
                  <option key={priority} value={priority}>
                    {CASE_PRIORITY_LABELS[priority]}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="case_number" className="block text-sm font-medium text-gray-700">
              Case number
            </label>
            <input id="case_number" className={inputClass} {...register('case_number')} />
          </div>

          <div>
            <label htmlFor="summary" className="block text-sm font-medium text-gray-700">
              Summary
            </label>
            <textarea id="summary" rows={3} className={inputClass} {...register('summary')} />
          </div>

          <div>
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
              Notes
            </label>
            <textarea id="notes" rows={4} className={inputClass} {...register('notes')} />
          </div>

          {error ? (
            <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>
          ) : null}

          <div className="flex gap-2 pt-2">
            <Button type="submit" loading={isSubmitting || mutation.isPending}>
              {mode === 'create' ? 'Create case' : 'Save changes'}
            </Button>
            <Link to={caseId ? `/cases/${caseId}` : '/cases'}>
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
