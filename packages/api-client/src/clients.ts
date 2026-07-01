import { apiPath, request } from './http';
import type { PaginatedResponse } from '@verdin/shared';

export type ClientStatus = 'active' | 'inactive';

export type ContactRelationship = 'primary' | 'spouse' | 'attorney' | 'authorized' | 'other';

export interface Client {
  id: string;
  organization_id: string;
  display_name: string;
  email: string | null;
  phone: string | null;
  status: ClientStatus;
  notes: string | null;
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
  status?: ClientStatus;
  notes?: string | null;
}

export interface UpdateClientInput {
  display_name?: string;
  email?: string | null;
  phone?: string | null;
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
