import { apiPath, request } from './http';

import type { OrganizationBillingSummary } from './billing';

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
  billing?: OrganizationBillingSummary | null;
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
    body: input,
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

export interface ApiKeyRateLimitStatus {
  enabled: boolean;
  limit_per_minute: number;
  backend: string;
}

export interface ApiKeyRotateResponse {
  api_key: string;
  previous_key: ApiKey;
  new_key: ApiKey;
}

export interface DeveloperPortal {
  enabled: boolean;
  ready: boolean;
  rotation_enabled: boolean;
  blockers: string[];
  active_api_key_count: number;
  rate_limit: ApiKeyRateLimitStatus;
  api_keys: ApiKey[];
}

export type OAuthDeveloperAppStatus = 'pending_approval' | 'approved' | 'revoked' | 'failed';

export interface OAuthDeveloperApp {
  id: string;
  organization_id: string;
  name: string;
  redirect_uri: string;
  scopes: string[];
  status: OAuthDeveloperAppStatus;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  revoked_at: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface OAuthDeveloperAppCreateInput {
  name: string;
  redirect_uri: string;
  scopes?: string[];
}

export function getApiKeyRateLimitStatus() {
  return request<ApiKeyRateLimitStatus>(apiPath('/org-admin/api-keys/rate-limit/status'));
}

export function getDeveloperPortal() {
  return request<DeveloperPortal>(apiPath('/org-admin/developer-portal'));
}

export function rotateOrganizationApiKey(apiKeyId: string) {
  return request<ApiKeyRotateResponse>(apiPath(`/org-admin/api-keys/${apiKeyId}/rotate`), {
    method: 'POST',
  });
}

export function listOAuthDeveloperApps() {
  return request<OAuthDeveloperApp[]>(apiPath('/org-admin/developer-portal/oauth-apps'));
}

export function createOAuthDeveloperApp(input: OAuthDeveloperAppCreateInput) {
  return request<OAuthDeveloperApp>(apiPath('/org-admin/developer-portal/oauth-apps'), {
    method: 'POST',
    body: input,
  });
}

export function approveOAuthDeveloperApp(appId: string) {
  return request<OAuthDeveloperApp>(
    apiPath(`/org-admin/developer-portal/oauth-apps/${appId}/approve`),
    {
      method: 'POST',
    },
  );
}

export type OAuthMarketplacePublishingRunStatus =
  'pending_approval' | 'approved' | 'rejected' | 'failed';

export interface OAuthMarketplacePublishingGateStatus {
  enabled: boolean;
  ready: boolean;
  public_oauth_developer_portal_ready: boolean;
  blockers: string[];
}

export interface OAuthMarketplacePublishingRun {
  id: string;
  organization_id: string;
  oauth_developer_app_id: string;
  entity_id: string;
  status: OAuthMarketplacePublishingRunStatus;
  publishing_summary: string;
  marketplace_listing_slug: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  error_message: string | null;
}

export interface OAuthMarketplacePublishingSubmitInput {
  publishing_summary: string;
  marketplace_listing_slug: string;
}

export interface OAuthMarketplacePublishingRunResult {
  completed_at: string;
  run: OAuthMarketplacePublishingRun;
}

export interface OAuthMarketplacePublishingRunList {
  items: OAuthMarketplacePublishingRun[];
  total: number;
  page: number;
  page_size: number;
}

export function getOAuthMarketplacePublishingStatus() {
  return request<OAuthMarketplacePublishingGateStatus>(
    apiPath('/org-admin/developer-portal/oauth-marketplace-publishing/status'),
  );
}

export function listOAuthMarketplacePublishingRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<OAuthMarketplacePublishingRunList>(
    apiPath(`/org-admin/developer-portal/oauth-marketplace-publishing/runs?${params}`),
  );
}

export function startOAuthMarketplacePublishingFromApp(
  oauthDeveloperAppId: string,
  input: OAuthMarketplacePublishingSubmitInput,
) {
  return request<OAuthMarketplacePublishingRunResult>(
    apiPath(
      `/org-admin/developer-portal/oauth-marketplace-publishing/oauth-apps/${oauthDeveloperAppId}/start`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveOAuthMarketplacePublishingRun(runId: string) {
  return request<OAuthMarketplacePublishingRunResult>(
    apiPath(`/org-admin/developer-portal/oauth-marketplace-publishing/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
