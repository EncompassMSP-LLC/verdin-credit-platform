import { apiPath, request, uploadRequest } from './http';
import type { PaginatedResponse } from '@verdin/shared';
import type { Document } from './documents';

export type ClientStatus = 'active' | 'inactive';

export type ContactRelationship = 'primary' | 'spouse' | 'attorney' | 'authorized' | 'other';

export interface Client {
  id: string;
  organization_id: string;
  display_name: string;
  email: string | null;
  phone: string | null;
  mailing_address_line1: string | null;
  mailing_address_line2: string | null;
  mailing_city: string | null;
  mailing_state: string | null;
  mailing_postal_code: string | null;
  status: ClientStatus;
  notes: string | null;
  identity_document_id: string | null;
  proof_of_address_document_id: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface ClientContact {
  id: string;
  organization_id: string;
  client_id: string;
  full_name: string;
  email: string | null;
  phone: string | null;
  relationship_type: ContactRelationship;
  is_primary: boolean;
  notes: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateClientInput {
  display_name: string;
  email?: string | null;
  phone?: string | null;
  mailing_address_line1: string;
  mailing_address_line2?: string | null;
  mailing_city: string;
  mailing_state: string;
  mailing_postal_code: string;
  status?: ClientStatus;
  notes?: string | null;
}

export interface UpdateClientInput {
  display_name?: string;
  email?: string | null;
  phone?: string | null;
  mailing_address_line1?: string | null;
  mailing_address_line2?: string | null;
  mailing_city?: string | null;
  mailing_state?: string | null;
  mailing_postal_code?: string | null;
  status?: ClientStatus;
  notes?: string | null;
}

export interface ListClientsParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: ClientStatus;
  sort_by?: 'created_at' | 'updated_at' | 'display_name' | 'status';
  sort_order?: 'asc' | 'desc';
}

export interface CreateClientContactInput {
  full_name: string;
  email?: string | null;
  phone?: string | null;
  relationship_type?: ContactRelationship;
  is_primary?: boolean;
  notes?: string | null;
}

export interface UpdateClientContactInput {
  full_name?: string;
  email?: string | null;
  phone?: string | null;
  relationship_type?: ContactRelationship;
  is_primary?: boolean;
  notes?: string | null;
}

export interface ListClientContactsParams {
  page?: number;
  page_size?: number;
  search?: string;
  relationship_type?: ContactRelationship;
  is_primary?: boolean;
  sort_by?: 'created_at' | 'updated_at' | 'full_name' | 'relationship';
  sort_order?: 'asc' | 'desc';
}

function buildQuery(params: ListClientsParams | ListClientContactsParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function createClient(input: CreateClientInput): Promise<Client> {
  return request<Client>(apiPath('/clients'), { method: 'POST', body: input });
}

export async function listClients(
  params: ListClientsParams = {},
): Promise<PaginatedResponse<Client>> {
  return request<PaginatedResponse<Client>>(`${apiPath('/clients')}${buildQuery(params)}`);
}

export async function getClient(clientId: string): Promise<Client> {
  return request<Client>(apiPath(`/clients/${clientId}`));
}

export async function updateClient(clientId: string, input: UpdateClientInput): Promise<Client> {
  return request<Client>(apiPath(`/clients/${clientId}`), { method: 'PATCH', body: input });
}

export async function deleteClient(clientId: string): Promise<void> {
  await request<void>(apiPath(`/clients/${clientId}`), { method: 'DELETE' });
}

export async function uploadClientIdentityDocument(
  clientId: string,
  caseId: string,
  file: File,
  title?: string,
): Promise<Document> {
  const form = new FormData();
  form.append('file', file);
  form.append('case_id', caseId);
  if (title) form.append('title', title);
  return uploadRequest<Document>(apiPath(`/clients/${clientId}/identity-document`), form);
}

export async function uploadClientProofOfAddressDocument(
  clientId: string,
  caseId: string,
  file: File,
  title?: string,
): Promise<Document> {
  const form = new FormData();
  form.append('file', file);
  form.append('case_id', caseId);
  if (title) form.append('title', title);
  return uploadRequest<Document>(apiPath(`/clients/${clientId}/proof-of-address-document`), form);
}

export async function createClientContact(
  clientId: string,
  input: CreateClientContactInput,
): Promise<ClientContact> {
  return request<ClientContact>(apiPath(`/clients/${clientId}/contacts`), {
    method: 'POST',
    body: input,
  });
}

export async function listClientContacts(
  clientId: string,
  params: ListClientContactsParams = {},
): Promise<PaginatedResponse<ClientContact>> {
  return request<PaginatedResponse<ClientContact>>(
    `${apiPath(`/clients/${clientId}/contacts`)}${buildQuery(params)}`,
  );
}

export async function getClientContact(
  clientId: string,
  contactId: string,
): Promise<ClientContact> {
  return request<ClientContact>(apiPath(`/clients/${clientId}/contacts/${contactId}`));
}

export async function updateClientContact(
  clientId: string,
  contactId: string,
  input: UpdateClientContactInput,
): Promise<ClientContact> {
  return request<ClientContact>(apiPath(`/clients/${clientId}/contacts/${contactId}`), {
    method: 'PATCH',
    body: input,
  });
}

export async function deleteClientContact(clientId: string, contactId: string): Promise<void> {
  await request<void>(apiPath(`/clients/${clientId}/contacts/${contactId}`), { method: 'DELETE' });
}

export type PreferredCommunicationChannel = 'mail' | 'phone' | 'email' | 'text';
export type AttorneyRepresentationStatus = 'none' | 'represented' | 'unknown';
export type DncAssistanceStatus =
  | 'not_started'
  | 'consent_recorded'
  | 'registry_link_opened'
  | 'awaiting_email_confirmation'
  | 'completed'
  | 'abandoned';

export interface PreferenceEventItem {
  at: string;
  action: string;
  actor_id?: string | null;
  detail?: string | null;
}

export interface ClientCommunicationPreferences {
  id: string;
  organization_id: string;
  client_id: string;
  preferred_channel: PreferredCommunicationChannel;
  do_not_text: boolean;
  do_not_email: boolean;
  best_calling_hours: string | null;
  workplace_calls_prohibited: boolean;
  attorney_representation_status: AttorneyRepresentationStatus;
  collector_opt_out_recorded: boolean;
  collector_opt_out_recorded_at: string | null;
  dnc_assistance_requested: boolean;
  dnc_consent_attested: boolean;
  dnc_phone_ownership_confirmed: boolean;
  dnc_disclosure_acknowledged: boolean;
  dnc_phone_number: string | null;
  dnc_status: DncAssistanceStatus;
  dnc_registry_opened_at: string | null;
  dnc_completed_at: string | null;
  dnc_followup_due_at: string | null;
  preference_events: PreferenceEventItem[];
  notes: string | null;
  official_dnc_registry_url: string;
  dnc_disclosure: string;
  disclaimer: string;
  communication_request_draft: string;
  created_at: string;
  updated_at: string;
}

export interface UpdateClientCommunicationPreferencesInput {
  preferred_channel?: PreferredCommunicationChannel;
  do_not_text?: boolean;
  do_not_email?: boolean;
  best_calling_hours?: string | null;
  workplace_calls_prohibited?: boolean;
  attorney_representation_status?: AttorneyRepresentationStatus;
  collector_opt_out_recorded?: boolean;
  dnc_assistance_requested?: boolean;
  dnc_consent_attested?: boolean;
  dnc_phone_ownership_confirmed?: boolean;
  dnc_disclosure_acknowledged?: boolean;
  dnc_phone_number?: string | null;
  notes?: string | null;
}

export async function getClientCommunicationPreferences(
  clientId: string,
): Promise<ClientCommunicationPreferences> {
  return request<ClientCommunicationPreferences>(
    apiPath(`/clients/${clientId}/communication-preferences`),
  );
}

export async function updateClientCommunicationPreferences(
  clientId: string,
  input: UpdateClientCommunicationPreferencesInput,
): Promise<ClientCommunicationPreferences> {
  return request<ClientCommunicationPreferences>(
    apiPath(`/clients/${clientId}/communication-preferences`),
    { method: 'PUT', body: input },
  );
}

export async function openClientDncRegistry(
  clientId: string,
): Promise<ClientCommunicationPreferences> {
  return request<ClientCommunicationPreferences>(
    apiPath(`/clients/${clientId}/communication-preferences/do-not-call/open-registry`),
    { method: 'POST' },
  );
}

export async function markClientDncCompleted(
  clientId: string,
): Promise<ClientCommunicationPreferences> {
  return request<ClientCommunicationPreferences>(
    apiPath(`/clients/${clientId}/communication-preferences/do-not-call/mark-completed`),
    { method: 'POST' },
  );
}
