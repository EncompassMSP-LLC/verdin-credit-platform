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

export interface BureauBenchmarkWindow {
  baseline_days: number;
  recent_days: number;
}

export interface OrganizationDisputeSettings {
  organization_id: string;
  cross_bureau_balance_tolerance: string;
  platform_default_tolerance: string;
  reinvestigation_benchmark_baseline_days: number;
  reinvestigation_benchmark_recent_days: number;
  reinvestigation_benchmark_bureau_windows: Record<string, BureauBenchmarkWindow>;
  reinvestigation_benchmark_recipient_windows: Record<string, BureauBenchmarkWindow>;
  platform_default_baseline_days: number;
  platform_default_recent_days: number;
  updated_at: string | null;
}

export interface OrganizationDisputeSettingsUpdateInput {
  cross_bureau_balance_tolerance?: string;
  reinvestigation_benchmark_baseline_days?: number;
  reinvestigation_benchmark_recent_days?: number;
  reinvestigation_benchmark_bureau_windows?: Record<string, BureauBenchmarkWindow | null>;
  reinvestigation_benchmark_recipient_windows?: Record<string, BureauBenchmarkWindow | null>;
}

export function getOrganizationDisputeSettings() {
  return request<OrganizationDisputeSettings>(apiPath('/org-admin/dispute-settings'));
}

export function updateOrganizationDisputeSettings(input: OrganizationDisputeSettingsUpdateInput) {
  return request<OrganizationDisputeSettings>(apiPath('/org-admin/dispute-settings'), {
    method: 'PATCH',
    body: input,
  });
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

export type PublicOAuthMarketplaceListingRunStatus =
  'pending_approval' | 'listed' | 'rejected' | 'failed';

export interface PublicOAuthMarketplaceListingGateStatus {
  enabled: boolean;
  ready: boolean;
  oauth_marketplace_publishing_ready: boolean;
  blockers: string[];
}

export interface PublicOAuthMarketplaceListingRun {
  id: string;
  organization_id: string;
  oauth_marketplace_publishing_run_id: string;
  oauth_developer_app_id: string;
  entity_id: string;
  status: PublicOAuthMarketplaceListingRunStatus;
  listing_summary: string;
  marketplace_listing_slug: string;
  public_listing_url: string | null;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  listed_at: string | null;
  error_message: string | null;
}

export interface PublicOAuthMarketplaceListingSubmitInput {
  listing_summary: string;
  public_listing_url?: string | null;
}

export interface PublicOAuthMarketplaceListingRunResult {
  completed_at: string;
  run: PublicOAuthMarketplaceListingRun;
}

export interface PublicOAuthMarketplaceListingRunList {
  items: PublicOAuthMarketplaceListingRun[];
  total: number;
  page: number;
  page_size: number;
}

export function getPublicOAuthMarketplaceListingStatus() {
  return request<PublicOAuthMarketplaceListingGateStatus>(
    apiPath('/org-admin/developer-portal/public-oauth-marketplace-listings/status'),
  );
}

export function listPublicOAuthMarketplaceListingRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<PublicOAuthMarketplaceListingRunList>(
    apiPath(`/org-admin/developer-portal/public-oauth-marketplace-listings/runs?${params}`),
  );
}

export function startPublicOAuthMarketplaceListingFromPublishingRun(
  oauthMarketplacePublishingRunId: string,
  input: PublicOAuthMarketplaceListingSubmitInput,
) {
  return request<PublicOAuthMarketplaceListingRunResult>(
    apiPath(
      `/org-admin/developer-portal/public-oauth-marketplace-listings/publishing-runs/${oauthMarketplacePublishingRunId}/start`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approvePublicOAuthMarketplaceListingRun(runId: string) {
  return request<PublicOAuthMarketplaceListingRunResult>(
    apiPath(`/org-admin/developer-portal/public-oauth-marketplace-listings/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
