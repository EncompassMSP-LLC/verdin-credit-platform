import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useParams } from 'react-router-dom';
import {
  createClientContact,
  deleteClient,
  deleteClientContact,
  getClient,
  getClientPortalUser,
  listClientContacts,
  provisionClientPortalUser,
  revokeClientPortalUser,
} from '@verdin/api-client';
import { createClientContactSchema, type CreateClientContactInput } from '@verdin/validation';
import { Button, Card } from '@verdin/ui';
import { ClientDisputeDocumentsCard } from '../../components/clients/ClientDisputeDocumentsCard';
import { ClientAccountsPanel } from '../../components/clients/ClientAccountsPanel';
import { ClientStatusBadge } from '../../components/clients/ClientStatusBadge';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

function formatMailingAddress(client: {
  mailing_address_line1: string | null;
  mailing_address_line2: string | null;
  mailing_city: string | null;
  mailing_state: string | null;
  mailing_postal_code: string | null;
}): string | null {
  const line1 = client.mailing_address_line1?.trim();
  if (!line1) return null;
  const lines = [line1];
  const line2 = client.mailing_address_line2?.trim();
  if (line2) lines.push(line2);
  const city = client.mailing_city?.trim() ?? '';
  const state = client.mailing_state?.trim() ?? '';
  const postal = client.mailing_postal_code?.trim() ?? '';
  const cityState = [city, state].filter(Boolean).join(', ');
  if (cityState && postal) lines.push(`${cityState} ${postal}`);
  else if (cityState) lines.push(cityState);
  else if (postal) lines.push(postal);
  return lines.join('\n');
}

export function ClientDetailPage() {
  const { clientId } = useParams<{ clientId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [portalEmail, setPortalEmail] = useState('');
  const [portalPassword, setPortalPassword] = useState('');
  const [portalError, setPortalError] = useState<string | null>(null);

  const clientQuery = useQuery({
    queryKey: ['client', clientId],
    queryFn: () => getClient(clientId!),
    enabled: Boolean(clientId),
  });

  const contactsQuery = useQuery({
    queryKey: ['client-contacts', clientId],
    queryFn: () => listClientContacts(clientId!, { page_size: 50 }),
    enabled: Boolean(clientId),
  });

  const portalQuery = useQuery({
    queryKey: ['client-portal-user', clientId],
    queryFn: () => getClientPortalUser(clientId!),
    enabled: Boolean(clientId) && featureFlags.enableClientPortal,
    retry: false,
  });

  const contactForm = useForm<CreateClientContactInput>({
    resolver: zodResolver(createClientContactSchema),
    defaultValues: {
      full_name: '',
      email: '',
      phone: '',
      relationship_type: 'primary',
      is_primary: false,
      notes: '',
    },
  });

  const addContactMutation = useMutation({
    mutationFn: (values: CreateClientContactInput) =>
      createClientContact(clientId!, {
        full_name: values.full_name,
        email: values.email || null,
        phone: values.phone || null,
        relationship_type: values.relationship_type,
        is_primary: values.is_primary,
        notes: values.notes || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-contacts', clientId] });
      contactForm.reset();
    },
  });

  const deleteContactMutation = useMutation({
    mutationFn: (contactId: string) => deleteClientContact(clientId!, contactId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-contacts', clientId] });
    },
  });

  const deleteClientMutation = useMutation({
    mutationFn: () => deleteClient(clientId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      navigate('/clients');
    },
  });

  const provisionPortalMutation = useMutation({
    mutationFn: () =>
      provisionClientPortalUser(clientId!, {
        email: portalEmail,
        password: portalPassword,
      }),
    onSuccess: () => {
      setPortalError(null);
      setPortalPassword('');
      queryClient.invalidateQueries({ queryKey: ['client-portal-user', clientId] });
    },
    onError: (err: Error) => setPortalError(err.message),
  });

  const revokePortalMutation = useMutation({
    mutationFn: () => revokeClientPortalUser(clientId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['client-portal-user', clientId] });
    },
  });

  if (clientQuery.isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading client…</p>
        </Card>
      </div>
    );
  }

  if (clientQuery.isError || !clientQuery.data) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-8 text-center text-sm text-red-600">
            {clientQuery.error instanceof Error ? clientQuery.error.message : 'Client not found'}
          </p>
        </Card>
      </div>
    );
  }

  const client = clientQuery.data;
  const mailingAddress = formatMailingAddress(client);

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/clients" className="text-sm text-brand-600 hover:underline">
            ← Back to clients
          </Link>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <h1 className="text-2xl font-bold text-gray-900">{client.display_name}</h1>
            <ClientStatusBadge status={client.status} />
          </div>
          <p className="mt-2 text-sm text-gray-600">
            {client.email ?? 'No email'} · {client.phone ?? 'No phone'}
          </p>
          {mailingAddress ? (
            <p className="mt-2 whitespace-pre-line text-sm text-gray-600">{mailingAddress}</p>
          ) : (
            <p className="mt-2 text-sm text-amber-700">
              Mailing address missing — edit client to add address for consent documents.
            </p>
          )}
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/clients/${client.id}/edit`}>
            <Button variant="secondary">Edit</Button>
          </Link>
          {confirmDelete ? (
            <>
              <Button variant="secondary" onClick={() => setConfirmDelete(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => deleteClientMutation.mutate()}
                disabled={deleteClientMutation.isPending}
              >
                Confirm delete
              </Button>
            </>
          ) : (
            <Button variant="secondary" onClick={() => setConfirmDelete(true)}>
              Delete
            </Button>
          )}
        </div>
      </div>

      <ClientDisputeDocumentsCard
        clientId={client.id}
        identityDocumentId={client.identity_document_id}
        proofOfAddressDocumentId={client.proof_of_address_document_id}
      />

      <ClientAccountsPanel clientId={client.id} />

      <div className="mt-8 grid grid-cols-1 gap-8 xl:grid-cols-2">
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-gray-900">Profile</h2>
          {client.notes ? (
            <p className="mt-4 whitespace-pre-wrap text-sm text-gray-700">{client.notes}</p>
          ) : (
            <p className="mt-4 text-sm text-gray-500">No notes on file.</p>
          )}
        </Card>

        {featureFlags.enableClientPortal ? (
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-gray-900">Client portal</h2>
            {portalQuery.isLoading ? (
              <p className="mt-4 text-sm text-gray-500">Checking portal access…</p>
            ) : portalQuery.isError ? (
              <div className="mt-4 space-y-3">
                <p className="text-sm text-gray-600">No portal user provisioned yet.</p>
                <div>
                  <label className="text-sm font-medium text-gray-700">Portal email</label>
                  <input
                    className={inputClass}
                    type="email"
                    value={portalEmail}
                    onChange={(event) => setPortalEmail(event.target.value)}
                    placeholder={client.email ?? 'client@example.com'}
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-700">Temporary password</label>
                  <input
                    className={inputClass}
                    type="password"
                    value={portalPassword}
                    onChange={(event) => setPortalPassword(event.target.value)}
                  />
                </div>
                {portalError ? <p className="text-sm text-red-600">{portalError}</p> : null}
                <Button
                  onClick={() => provisionPortalMutation.mutate()}
                  disabled={
                    provisionPortalMutation.isPending || !portalEmail || portalPassword.length < 8
                  }
                >
                  Provision portal user
                </Button>
              </div>
            ) : portalQuery.data ? (
              <div className="mt-4 space-y-2 text-sm text-gray-700">
                <p>
                  <span className="font-medium">Email:</span> {portalQuery.data.email}
                </p>
                <p>
                  <span className="font-medium">Status:</span>{' '}
                  {portalQuery.data.is_active ? 'Active' : 'Inactive'}
                </p>
                <Button
                  variant="secondary"
                  className="mt-3"
                  onClick={() => revokePortalMutation.mutate()}
                  disabled={revokePortalMutation.isPending}
                >
                  Revoke portal access
                </Button>
              </div>
            ) : null}
          </Card>
        ) : null}
      </div>

      <Card className="mt-8 p-6">
        <h2 className="text-lg font-semibold text-gray-900">Contacts</h2>
        <div className="mt-4 space-y-3">
          {contactsQuery.data?.items.length ? (
            contactsQuery.data.items.map((contact) => (
              <div
                key={contact.id}
                className="flex flex-col gap-2 rounded-md border border-gray-200 p-4 sm:flex-row sm:items-center sm:justify-between"
              >
                <div>
                  <p className="font-medium text-gray-900">
                    {contact.full_name}
                    {contact.is_primary ? (
                      <span className="ml-2 text-xs uppercase text-brand-600">Primary</span>
                    ) : null}
                  </p>
                  <p className="text-sm text-gray-600">
                    {contact.relationship_type}
                    {contact.email ? ` · ${contact.email}` : ''}
                    {contact.phone ? ` · ${contact.phone}` : ''}
                  </p>
                </div>
                <Button
                  variant="secondary"
                  onClick={() => deleteContactMutation.mutate(contact.id)}
                  disabled={deleteContactMutation.isPending}
                >
                  Remove
                </Button>
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No contacts yet.</p>
          )}
        </div>

        <form
          className="mt-6 grid grid-cols-1 gap-4 border-t border-gray-200 pt-6 md:grid-cols-2"
          onSubmit={contactForm.handleSubmit((values) => addContactMutation.mutate(values))}
        >
          <div className="md:col-span-2">
            <label className="text-sm font-medium text-gray-700">Add contact</label>
          </div>
          <div>
            <input
              className={inputClass}
              placeholder="Full name"
              {...contactForm.register('full_name')}
            />
            {contactForm.formState.errors.full_name ? (
              <p className="mt-1 text-sm text-red-600">
                {contactForm.formState.errors.full_name.message}
              </p>
            ) : null}
          </div>
          <div>
            <select className={inputClass} {...contactForm.register('relationship_type')}>
              <option value="primary">Primary</option>
              <option value="spouse">Spouse</option>
              <option value="attorney">Attorney</option>
              <option value="authorized">Authorized</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <input
              type="email"
              className={inputClass}
              placeholder="Email"
              {...contactForm.register('email')}
            />
          </div>
          <div>
            <input className={inputClass} placeholder="Phone" {...contactForm.register('phone')} />
          </div>
          <div className="flex items-center gap-2 md:col-span-2">
            <input type="checkbox" {...contactForm.register('is_primary')} />
            <span className="text-sm text-gray-700">Primary contact</span>
          </div>
          <div className="md:col-span-2">
            <Button type="submit" disabled={addContactMutation.isPending}>
              Add contact
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
