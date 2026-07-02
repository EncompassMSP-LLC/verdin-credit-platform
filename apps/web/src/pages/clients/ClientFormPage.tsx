import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import { createClient, updateClient } from '@verdin/api-client';
import {
  createClientSchema,
  type CreateClientInput,
  type UpdateClientInput,
} from '@verdin/validation';
import { Button, Card } from '@verdin/ui';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface ClientFormPageProps {
  mode: 'create' | 'edit';
  clientId?: string;
  defaultValues?: CreateClientInput;
}

export function ClientFormPage({ mode, clientId, defaultValues }: ClientFormPageProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateClientInput>({
    resolver: zodResolver(createClientSchema),
    defaultValues: defaultValues ?? {
      display_name: '',
      email: '',
      phone: '',
      status: 'active',
      notes: '',
    },
  });

  const mutation = useMutation({
    mutationFn: async (values: CreateClientInput) => {
      const payload = {
        display_name: values.display_name,
        email: values.email || null,
        phone: values.phone || null,
        status: values.status,
        notes: values.notes || null,
      };
      if (mode === 'create') {
        return createClient(payload);
      }
      if (!clientId) throw new Error('Client ID is required');
      return updateClient(clientId, payload as UpdateClientInput);
    },
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['client', result.id] });
      navigate(`/clients/${result.id}`);
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
          to={clientId ? `/clients/${clientId}` : '/clients'}
          className="text-sm text-brand-600 hover:underline"
        >
          ← Back to {clientId ? 'client' : 'clients'}
        </Link>
        <h1 className="mt-4 text-2xl font-bold text-gray-900">
          {mode === 'create' ? 'New client' : 'Edit client'}
        </h1>
      </div>

      <Card className="max-w-2xl p-6">
        <form onSubmit={onSubmit} className="space-y-5">
          <div>
            <label className="text-sm font-medium text-gray-700">Display name</label>
            <input className={inputClass} {...register('display_name')} />
            {errors.display_name ? (
              <p className="mt-1 text-sm text-red-600">{errors.display_name.message}</p>
            ) : null}
          </div>

          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <div>
              <label className="text-sm font-medium text-gray-700">Email</label>
              <input type="email" className={inputClass} {...register('email')} />
              {errors.email ? (
                <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
              ) : null}
            </div>
            <div>
              <label className="text-sm font-medium text-gray-700">Phone</label>
              <input className={inputClass} {...register('phone')} />
            </div>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Status</label>
            <select className={inputClass} {...register('status')}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Notes</label>
            <textarea rows={4} className={inputClass} {...register('notes')} />
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          <div className="flex gap-3">
            <Button type="submit" disabled={isSubmitting || mutation.isPending}>
              {mode === 'create' ? 'Create client' : 'Save changes'}
            </Button>
            <Link to={clientId ? `/clients/${clientId}` : '/clients'}>
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
