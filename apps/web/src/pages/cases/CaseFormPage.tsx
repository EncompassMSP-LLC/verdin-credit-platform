import { useState } from 'react';
import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  createCase,
  createClient,
  updateCase,
  uploadCaseIdentityDocument,
} from '@verdin/api-client';
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
import { ClientPicker } from '../../components/cases/ClientPicker';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

interface CaseFormPageProps {
  mode: 'create' | 'edit';
  caseId?: string;
  defaultValues?: CreateCaseInput;
}

type ClientAssociationMode = 'existing' | 'new' | 'manual';

interface NewClientDraft {
  display_name: string;
  email: string;
  phone: string;
  mailing_address_line1: string;
  mailing_address_line2: string;
  mailing_city: string;
  mailing_state: string;
  mailing_postal_code: string;
}

export function CaseFormPage({ mode, caseId, defaultValues }: CaseFormPageProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [identityFile, setIdentityFile] = useState<File | null>(null);
  const [clientMode, setClientMode] = useState<ClientAssociationMode>(
    defaultValues?.client_id ? 'existing' : 'manual',
  );
  const [newClient, setNewClient] = useState<NewClientDraft>({
    display_name: '',
    email: '',
    phone: '',
    mailing_address_line1: '',
    mailing_address_line2: '',
    mailing_city: '',
    mailing_state: '',
    mailing_postal_code: '',
  });

  const {
    register,
    handleSubmit,
    control,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CreateCaseInput>({
    resolver: zodResolver(createCaseSchema),
    defaultValues: defaultValues ?? {
      title: '',
      client_id: '',
      client_name: '',
      client_email: '',
      status: 'open',
      stage: 'intake',
      priority: 'medium',
      summary: '',
      notes: '',
    },
  });

  const linkedClientId = watch('client_id');
  const hasLinkedClient = clientMode === 'existing' && Boolean(linkedClientId);

  const mutation = useMutation({
    mutationFn: async (values: CreateCaseInput) => {
      let linkedClientIdValue = values.client_id || null;
      let clientNameValue = values.client_name?.trim() || undefined;
      let clientEmailValue = values.client_email || null;

      if (clientMode === 'new') {
        const createdClient = await createClient({
          display_name: newClient.display_name.trim(),
          email: newClient.email.trim() || null,
          phone: newClient.phone.trim() || null,
          mailing_address_line1: newClient.mailing_address_line1.trim(),
          mailing_address_line2: newClient.mailing_address_line2.trim() || null,
          mailing_city: newClient.mailing_city.trim(),
          mailing_state: newClient.mailing_state.trim(),
          mailing_postal_code: newClient.mailing_postal_code.trim(),
          status: 'active',
          notes: null,
        });
        linkedClientIdValue = createdClient.id;
        clientNameValue = createdClient.display_name;
        clientEmailValue = createdClient.email;
      }

      const payload = {
        ...values,
        client_id: linkedClientIdValue,
        client_name: clientNameValue,
        client_email: clientEmailValue,
      };
      if (mode === 'create') {
        return createCase(payload);
      }
      if (!caseId) throw new Error('Case ID is required');
      return updateCase(caseId, payload as UpdateCaseInput);
    },
    onSuccess: async (result) => {
      if (identityFile) {
        await uploadCaseIdentityDocument(result.id, identityFile, "Driver's license");
      }
      queryClient.invalidateQueries({ queryKey: ['cases'] });
      queryClient.invalidateQueries({ queryKey: ['case', result.id] });
      navigate(`/cases/${result.id}`);
    },
    onError: (err: Error) => setError(err.message),
  });

  const onSubmit = handleSubmit((values) => {
    if (clientMode === 'existing' && !values.client_id) {
      setError('Select an existing client or switch to New client / Manual.');
      return;
    }
    if (clientMode === 'new') {
      if (
        !newClient.display_name.trim() ||
        !newClient.mailing_address_line1.trim() ||
        !newClient.mailing_city.trim() ||
        !newClient.mailing_state.trim() ||
        !newClient.mailing_postal_code.trim()
      ) {
        setError('New client requires name and full mailing address.');
        return;
      }
      setValue('client_id', '', { shouldValidate: true });
      setValue('client_name', newClient.display_name.trim(), { shouldValidate: true });
      setValue('client_email', newClient.email.trim(), { shouldValidate: true });
    }
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

          <div className="space-y-2 rounded-md border border-gray-200 bg-gray-50 p-4">
            <p className="text-sm font-medium text-gray-700">Client association</p>
            <div className="flex flex-wrap gap-4 text-sm">
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="client-mode"
                  checked={clientMode === 'existing'}
                  onChange={() => {
                    setClientMode('existing');
                  }}
                />
                Existing client
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="client-mode"
                  checked={clientMode === 'new'}
                  onChange={() => {
                    setClientMode('new');
                    setValue('client_id', '', { shouldValidate: true });
                  }}
                />
                New client
              </label>
              <label className="inline-flex items-center gap-2">
                <input
                  type="radio"
                  name="client-mode"
                  checked={clientMode === 'manual'}
                  onChange={() => {
                    setClientMode('manual');
                    setValue('client_id', '', { shouldValidate: true });
                  }}
                />
                Manual entry
              </label>
            </div>
            {clientMode === 'existing' ? (
              <Controller
                name="client_id"
                control={control}
                render={({ field }) => (
                  <ClientPicker
                    value={field.value ?? ''}
                    onChange={(clientId, client) => {
                      field.onChange(clientId);
                      if (client) {
                        setValue('client_name', client.display_name, { shouldValidate: true });
                        setValue('client_email', client.email ?? '', { shouldValidate: true });
                      }
                    }}
                  />
                )}
              />
            ) : null}
            {clientMode === 'new' ? (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="block text-sm font-medium text-gray-700">New client name</label>
                  <input
                    className={inputClass}
                    value={newClient.display_name}
                    onChange={(event) =>
                      setNewClient((prev) => ({ ...prev, display_name: event.target.value }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    New client email
                  </label>
                  <input
                    type="email"
                    className={inputClass}
                    value={newClient.email}
                    onChange={(event) =>
                      setNewClient((prev) => ({ ...prev, email: event.target.value }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    New client phone
                  </label>
                  <input
                    className={inputClass}
                    value={newClient.phone}
                    onChange={(event) =>
                      setNewClient((prev) => ({ ...prev, phone: event.target.value }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Street address</label>
                  <input
                    className={inputClass}
                    value={newClient.mailing_address_line1}
                    onChange={(event) =>
                      setNewClient((prev) => ({
                        ...prev,
                        mailing_address_line1: event.target.value,
                      }))
                    }
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Apartment / suite (optional)
                  </label>
                  <input
                    className={inputClass}
                    value={newClient.mailing_address_line2}
                    onChange={(event) =>
                      setNewClient((prev) => ({
                        ...prev,
                        mailing_address_line2: event.target.value,
                      }))
                    }
                  />
                </div>
                <div className="grid grid-cols-3 gap-2 md:col-span-2">
                  <input
                    className={inputClass}
                    placeholder="City"
                    value={newClient.mailing_city}
                    onChange={(event) =>
                      setNewClient((prev) => ({ ...prev, mailing_city: event.target.value }))
                    }
                  />
                  <input
                    className={inputClass}
                    placeholder="State"
                    value={newClient.mailing_state}
                    onChange={(event) =>
                      setNewClient((prev) => ({ ...prev, mailing_state: event.target.value }))
                    }
                  />
                  <input
                    className={inputClass}
                    placeholder="ZIP"
                    value={newClient.mailing_postal_code}
                    onChange={(event) =>
                      setNewClient((prev) => ({
                        ...prev,
                        mailing_postal_code: event.target.value,
                      }))
                    }
                  />
                </div>
              </div>
            ) : null}
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">
                Client name {hasLinkedClient ? '(from linked client)' : ''}
              </label>
              <input
                id="client_name"
                className={inputClass}
                disabled={hasLinkedClient}
                {...register('client_name')}
              />
              {errors.client_name ? (
                <p className="mt-1 text-sm text-red-600">{errors.client_name.message}</p>
              ) : null}
            </div>
            <div>
              <label htmlFor="client_email" className="block text-sm font-medium text-gray-700">
                Client email {hasLinkedClient ? '(from linked client)' : ''}
              </label>
              <input
                id="client_email"
                type="email"
                className={inputClass}
                disabled={hasLinkedClient}
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

          <div>
            <label htmlFor="identity_document" className="block text-sm font-medium text-gray-700">
              Driver&apos;s license copy
            </label>
            <p className="mt-1 text-xs text-gray-500">
              Optional. Attached automatically to dispute mail packets for this case.
            </p>
            <input
              id="identity_document"
              type="file"
              accept="application/pdf,image/jpeg,image/png,image/tiff"
              className="mt-2 block w-full text-sm text-gray-700"
              onChange={(event) => setIdentityFile(event.target.files?.[0] ?? null)}
            />
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
