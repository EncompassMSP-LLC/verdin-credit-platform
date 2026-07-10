import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate } from 'react-router-dom';
import {
  createClient,
  listCases,
  updateClient,
  uploadClientIdentityDocument,
  uploadClientProofOfAddressDocument,
} from '@verdin/api-client';
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
  const [identityFile, setIdentityFile] = useState<File | null>(null);
  const [proofOfAddressFile, setProofOfAddressFile] = useState<File | null>(null);
  const [documentCaseId, setDocumentCaseId] = useState('');

  const clientCasesQuery = useQuery({
    queryKey: ['client-cases', clientId],
    queryFn: () => listCases({ client_id: clientId, page_size: 50 }),
    enabled: mode === 'edit' && Boolean(clientId),
  });

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
      mailing_address_line1: '',
      mailing_address_line2: '',
      mailing_city: '',
      mailing_state: '',
      mailing_postal_code: '',
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
        mailing_address_line1: values.mailing_address_line1,
        mailing_address_line2: values.mailing_address_line2 || null,
        mailing_city: values.mailing_city,
        mailing_state: values.mailing_state,
        mailing_postal_code: values.mailing_postal_code,
        status: values.status,
        notes: values.notes || null,
      };
      if (mode === 'create') {
        return createClient(payload);
      }
      if (!clientId) throw new Error('Client ID is required');
      return updateClient(clientId, payload as UpdateClientInput);
    },
    onSuccess: async (result) => {
      if (mode === 'edit' && documentCaseId) {
        if (identityFile) {
          await uploadClientIdentityDocument(
            result.id,
            documentCaseId,
            identityFile,
            "Driver's license",
          );
        }
        if (proofOfAddressFile) {
          await uploadClientProofOfAddressDocument(
            result.id,
            documentCaseId,
            proofOfAddressFile,
            'Proof of mailing address',
          );
        }
      }
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

          <div className="rounded-md border border-gray-200 bg-gray-50 p-4">
            <h2 className="text-sm font-semibold text-gray-900">Mailing address</h2>
            <p className="mt-1 text-xs text-gray-500">
              Used on CROA disclosures, service agreements, and dispute mail packets.
            </p>
            <div className="mt-4 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700">Street address</label>
                <input className={inputClass} {...register('mailing_address_line1')} />
                {errors.mailing_address_line1 ? (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.mailing_address_line1.message}
                  </p>
                ) : null}
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Apartment, suite, etc. (optional)
                </label>
                <input className={inputClass} {...register('mailing_address_line2')} />
              </div>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div>
                  <label className="text-sm font-medium text-gray-700">City</label>
                  <input className={inputClass} {...register('mailing_city')} />
                  {errors.mailing_city ? (
                    <p className="mt-1 text-sm text-red-600">{errors.mailing_city.message}</p>
                  ) : null}
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">State</label>
                  <input className={inputClass} {...register('mailing_state')} />
                  {errors.mailing_state ? (
                    <p className="mt-1 text-sm text-red-600">{errors.mailing_state.message}</p>
                  ) : null}
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">ZIP / postal code</label>
                  <input className={inputClass} {...register('mailing_postal_code')} />
                  {errors.mailing_postal_code ? (
                    <p className="mt-1 text-sm text-red-600">
                      {errors.mailing_postal_code.message}
                    </p>
                  ) : null}
                </div>
              </div>
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

          {mode === 'create' ? (
            <p className="text-sm text-gray-600">
              After creating this client, open their profile to upload a driver&apos;s license and
              proof of mailing address for dispute mail packets.
            </p>
          ) : (
            <div className="space-y-4 rounded-md border border-gray-200 bg-gray-50 p-4">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Dispute mail packet documents
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  Select a case, then upload documents to attach automatically to dispute mail
                  packets.
                </p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">Case</label>
                <select
                  className={inputClass}
                  value={documentCaseId}
                  onChange={(event) => setDocumentCaseId(event.target.value)}
                >
                  <option value="">Select a case…</option>
                  {(clientCasesQuery.data?.items ?? []).map((caseItem) => (
                    <option key={caseItem.id} value={caseItem.id}>
                      {caseItem.title}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Driver&apos;s license copy
                </label>
                <input
                  type="file"
                  accept="application/pdf,image/jpeg,image/png,image/tiff"
                  className="mt-2 block w-full text-sm text-gray-700"
                  onChange={(event) => setIdentityFile(event.target.files?.[0] ?? null)}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Proof of current mailing address
                </label>
                <p className="mt-1 text-xs text-gray-500">
                  Utility bill, bank statement, or other document showing the consumer&apos;s
                  current address.
                </p>
                <input
                  type="file"
                  accept="application/pdf,image/jpeg,image/png,image/tiff"
                  className="mt-2 block w-full text-sm text-gray-700"
                  onChange={(event) => setProofOfAddressFile(event.target.files?.[0] ?? null)}
                />
              </div>
            </div>
          )}

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
