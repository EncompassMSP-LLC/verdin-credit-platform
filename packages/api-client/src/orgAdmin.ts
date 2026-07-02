import { apiPath, request } from './http';

export type ApiKeyScope = 'read' | 'write';

export interface OrgAdminStatus {
  org_admin_enabled: boolean;
  api_keys_enabled: boolean;
  capabilities: string[];
  deferred_capabilities: string[];
}

export interface OrganizationAdminSummary {
  id: string;
  name: string;
  slug: string;
  is_active: boolean;
  active_user_count: number;
  active_api_key_count: number;
}

export interface ApiKey {
  id: string;
  organization_id: string;
  name: string;
  key_prefix: string;
  scopes: ApiKeyScope[];
  is_active: boolean;
  last_used_at: string | null;
  revoked_at: string | null;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface ApiKeyCreateInput {
  name: string;
  scopes?: ApiKeyScope[];
  expires_at?: string | null;
}

export interface ApiKeyCreateResponse extends ApiKey {
  api_key: string;
}

export function getOrgAdminStatus() {
  return request<OrgAdminStatus>(apiPath('/org-admin/status'));
}

export function getOrganizationAdminSummary() {
  return request<OrganizationAdminSummary>(apiPath('/org-admin/organization'));
}

export function listOrganizationApiKeys() {
  return request<ApiKey[]>(apiPath('/org-admin/api-keys'));
}

export function createOrganizationApiKey(input: ApiKeyCreateInput) {
  return request<ApiKeyCreateResponse>(apiPath('/org-admin/api-keys'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function getOrganizationApiKey(apiKeyId: string) {
  return request<ApiKey>(apiPath(`/org-admin/api-keys/${apiKeyId}`));
}

export function revokeOrganizationApiKey(apiKeyId: string) {
  return request<ApiKey>(apiPath(`/org-admin/api-keys/${apiKeyId}/revoke`), {
    method: 'POST',
  });
}
