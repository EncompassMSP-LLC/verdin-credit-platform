import { apiPath, request, uploadRequest } from './http';

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

export type PortalCaseStatus = 'open' | 'active' | 'on_hold' | 'resolved' | 'closed';
export type PortalCaseStage =
  | 'intake'
  | 'review'
  | 'evidence_gathering'
  | 'dispute_preparation'
  | 'awaiting_response'
  | 'monitoring'
  | 'complete';

export interface PortalCaseSummary {
  id: string;
  case_number: string | null;
  title: string;
  status: PortalCaseStatus;
  stage: PortalCaseStage;
  opened_at: string;
  closed_at: string | null;
  updated_at: string;
}

export interface PortalCaseDetail extends PortalCaseSummary {
  dispute_accounts: Record<string, number>;
  account_count: number;
}

export interface PortalCaseProgressResponse {
  items: PortalCaseSummary[];
}

export interface PortalDocument {
  id: string;
  case_id: string;
  title: string;
  description: string | null;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  processing_status: string;
  created_at: string;
}

export interface PortalCaseDocumentsResponse {
  items: PortalDocument[];
}

export interface UploadPortalCaseDocumentInput {
  file: File | Blob;
  title: string;
  description?: string | null;
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

export async function listPortalCases(): Promise<PortalCaseProgressResponse> {
  return request<PortalCaseProgressResponse>(apiPath('/portal/cases'));
}

export async function getPortalCase(caseId: string): Promise<PortalCaseDetail> {
  return request<PortalCaseDetail>(apiPath(`/portal/cases/${caseId}`));
}

export async function listPortalCaseDocuments(
  caseId: string,
): Promise<PortalCaseDocumentsResponse> {
  return request<PortalCaseDocumentsResponse>(apiPath(`/portal/cases/${caseId}/documents`));
}

export async function uploadPortalCaseDocument(
  caseId: string,
  input: UploadPortalCaseDocumentInput,
): Promise<PortalDocument> {
  const form = new FormData();
  form.append('file', input.file);
  form.append('title', input.title);
  if (input.description) form.append('description', input.description);
  return uploadRequest<PortalDocument>(apiPath(`/portal/cases/${caseId}/documents`), form);
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
