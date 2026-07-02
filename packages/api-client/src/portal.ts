import { apiPath, request } from './http';

export interface PortalLoginInput {
  email: string;
  password: string;
}

export interface PortalTokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface PortalMeResponse {
  id: string;
  organization_id: string;
  client_id: string;
  email: string;
  client_display_name: string;
  is_active: boolean;
  last_login_at: string | null;
}

export interface ClientPortalUser {
  id: string;
  organization_id: string;
  client_id: string;
  email: string;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProvisionPortalUserInput {
  email: string;
  password: string;
}

export interface UpdatePortalUserInput {
  email?: string;
  password?: string;
  is_active?: boolean;
}

export async function portalLogin(input: PortalLoginInput): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/login'), {
    method: 'POST',
    body: input,
    auth: false,
  });
}

export async function portalRefresh(refreshToken: string): Promise<PortalTokenResponse> {
  return request<PortalTokenResponse>(apiPath('/portal/auth/refresh'), {
    method: 'POST',
    body: { refresh_token: refreshToken },
    auth: false,
  });
}

export async function getPortalMe(): Promise<PortalMeResponse> {
  return request<PortalMeResponse>(apiPath('/portal/auth/me'));
}

export async function provisionClientPortalUser(
  clientId: string,
  input: ProvisionPortalUserInput,
): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`), {
    method: 'POST',
    body: input,
  });
}

export async function getClientPortalUser(clientId: string): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`));
}

export async function updateClientPortalUser(
  clientId: string,
  input: UpdatePortalUserInput,
): Promise<ClientPortalUser> {
  return request<ClientPortalUser>(apiPath(`/clients/${clientId}/portal-user`), {
    method: 'PATCH',
    body: input,
  });
}

export async function revokeClientPortalUser(clientId: string): Promise<void> {
  await request<void>(apiPath(`/clients/${clientId}/portal-user`), { method: 'DELETE' });
}
