import { apiPath, request } from './http';

export interface EnterpriseIdentityStatus {
  feature_enabled: boolean;
  sso_provider: string;
  sso_ready: boolean;
  mfa_mode: string;
  mfa_ready: boolean;
  ready: boolean;
  blockers: string[];
}

export interface TotpEnrollmentStart {
  secret: string;
  otpauth_url: string;
  issuer: string;
}

export interface TotpEnrollmentStatus {
  enrolled: boolean;
  enrolled_at: string | null;
  pending: boolean;
}

export interface SsoEnrollmentStart {
  authorization_url: string;
  state: string;
  provider: string;
}

export interface SsoEnrollmentStatus {
  linked: boolean;
  provider?: string | null;
  issuer_url?: string | null;
  linked_at?: string | null;
  idp_subject?: string | null;
}

export interface SsoEnrollmentCompleteInput {
  code: string;
  state: string;
}

export interface SsoEnrollmentComplete {
  linked: boolean;
  provider: string;
  issuer_url: string;
  idp_subject: string;
  linked_at: string;
  user_id: string;
}

export async function getEnterpriseIdentityStatus(): Promise<EnterpriseIdentityStatus> {
  return request<EnterpriseIdentityStatus>(apiPath('/enterprise/status'));
}

export function startTotpEnrollment() {
  return request<TotpEnrollmentStart>(apiPath('/enterprise/mfa/totp/enroll'), {
    method: 'POST',
  });
}

export function confirmTotpEnrollment(code: string) {
  return request<TotpEnrollmentStatus>(apiPath('/enterprise/mfa/totp/confirm'), {
    method: 'POST',
    body: JSON.stringify({ code }),
  });
}

export function getTotpEnrollmentStatus() {
  return request<TotpEnrollmentStatus>(apiPath('/enterprise/mfa/totp'));
}

export function disableTotpEnrollment() {
  return request<TotpEnrollmentStatus>(apiPath('/enterprise/mfa/totp'), {
    method: 'DELETE',
  });
}

export function startSsoEnrollment() {
  return request<SsoEnrollmentStart>(apiPath('/enterprise/sso/enrollment/start'), {
    method: 'POST',
  });
}

export function completeSsoEnrollment(input: SsoEnrollmentCompleteInput) {
  return request<SsoEnrollmentComplete>(apiPath('/enterprise/sso/enrollment/complete'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function getSsoEnrollmentStatus() {
  return request<SsoEnrollmentStatus>(apiPath('/enterprise/sso/enrollment'));
}

export interface ScimProvisioningStatus {
  enabled: boolean;
  ready: boolean;
  bearer_token_configured: boolean;
  blockers: string[];
}

export interface ScimMeta {
  resourceType: string;
  created?: string | null;
}

export interface ScimUserResource {
  schemas: string[];
  id: string;
  externalId: string;
  userName: string;
  active: boolean;
  meta: ScimMeta;
}

export interface ScimGroupResource {
  schemas: string[];
  id: string;
  externalId: string;
  displayName: string;
  meta: ScimMeta;
}

export interface ScimUserList {
  schemas: string[];
  totalResults: number;
  resources: ScimUserResource[];
}

export interface ScimGroupList {
  schemas: string[];
  totalResults: number;
  resources: ScimGroupResource[];
}

export interface ScimUserProvisionInput {
  userName: string;
  externalId: string;
  active?: boolean;
  name?: { givenName?: string; familyName?: string };
}

export interface ScimGroupProvisionInput {
  displayName: string;
  externalId: string;
}

export function getScimProvisioningStatus() {
  return request<ScimProvisioningStatus>(apiPath('/enterprise/scim/status'));
}

export function provisionScimUser(input: ScimUserProvisionInput) {
  return request<ScimUserResource>(apiPath('/enterprise/scim/v2/Users'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function listScimUsers() {
  return request<ScimUserList>(apiPath('/enterprise/scim/v2/Users'));
}

export function provisionScimGroup(input: ScimGroupProvisionInput) {
  return request<ScimGroupResource>(apiPath('/enterprise/scim/v2/Groups'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function listScimGroups() {
  return request<ScimGroupList>(apiPath('/enterprise/scim/v2/Groups'));
}

export interface IdpFederationStatus {
  enabled: boolean;
  ready: boolean;
  scim_provisioning_enabled: boolean;
  provider_count: number;
  blockers: string[];
}

export type IdpFederationProviderType = 'oidc' | 'saml';

export interface IdpFederationProvider {
  id: string;
  organization_id: string;
  provider_key: string;
  provider_type: IdpFederationProviderType;
  display_name: string;
  issuer_url: string | null;
  is_primary: boolean;
  enabled: boolean;
  registered_by_user_id: string | null;
}

export interface IdpFederationProviderList {
  total_results: number;
  providers: IdpFederationProvider[];
}

export interface IdpFederationProviderRegisterInput {
  provider_key: string;
  provider_type: IdpFederationProviderType;
  display_name: string;
  issuer_url?: string | null;
  is_primary?: boolean;
  enabled?: boolean;
}

export function getIdpFederationStatus() {
  return request<IdpFederationStatus>(apiPath('/enterprise/federation/status'));
}

export function listIdpFederationProviders() {
  return request<IdpFederationProviderList>(apiPath('/enterprise/federation/providers'));
}

export function registerIdpFederationProvider(input: IdpFederationProviderRegisterInput) {
  return request<IdpFederationProvider>(apiPath('/enterprise/federation/providers'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export type SamlMetadataValidationStatus = 'valid' | 'invalid';

export interface SamlFederationMetadataStatus {
  enabled: boolean;
  ready: boolean;
  federation_ready: boolean;
  blockers: string[];
}

export interface SamlFederationMetadataUpload {
  id: string;
  organization_id: string;
  provider_key: string | null;
  entity_id: string | null;
  validation_status: SamlMetadataValidationStatus;
  validation_message: string | null;
  uploaded_by_user_id: string | null;
  uploaded_at: string | null;
}

export interface SamlFederationMetadataUploadList {
  total: number;
  page: number;
  page_size: number;
  items: SamlFederationMetadataUpload[];
}

export interface SamlFederationMetadataUploadInput {
  metadata_xml: string;
  provider_key?: string | null;
}

export interface SamlFederationMetadataUploadResult {
  uploaded_at: string;
  upload: SamlFederationMetadataUpload;
}

export function getSamlFederationMetadataStatus() {
  return request<SamlFederationMetadataStatus>(
    apiPath('/enterprise/federation/saml-metadata/status'),
  );
}

export function listSamlFederationMetadataUploads(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<SamlFederationMetadataUploadList>(
    apiPath(`/enterprise/federation/saml-metadata/uploads?${params}`),
  );
}

export function uploadSamlFederationMetadata(input: SamlFederationMetadataUploadInput) {
  return request<SamlFederationMetadataUploadResult>(
    apiPath('/enterprise/federation/saml-metadata/upload'),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export type HrisBidirectionalSyncRunKind = 'employees_inbound' | 'employees_outbound';

export type HrisBidirectionalSyncRunStatus = 'pending' | 'running' | 'completed' | 'failed';

export type HrisBidirectionalSyncTriggerSource = 'manual' | 'scheduled';

export interface HrisBidirectionalSyncStatus {
  enabled: boolean;
  ready: boolean;
  saml_metadata_ready: boolean;
  blockers: string[];
}

export interface HrisBidirectionalSyncRun {
  id: string;
  organization_id: string;
  run_kind: HrisBidirectionalSyncRunKind;
  trigger_source: HrisBidirectionalSyncTriggerSource;
  status: HrisBidirectionalSyncRunStatus;
  records_synced: number;
  records_skipped: number;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface HrisBidirectionalSyncRunList {
  total: number;
  page: number;
  page_size: number;
  items: HrisBidirectionalSyncRun[];
}

export interface HrisBidirectionalSyncRunInput {
  run_kind?: HrisBidirectionalSyncRunKind;
}

export interface HrisBidirectionalSyncRunResult {
  completed_at: string;
  run: HrisBidirectionalSyncRun;
}

export function getHrisBidirectionalSyncStatus() {
  return request<HrisBidirectionalSyncStatus>(apiPath('/enterprise/federation/hris-sync/status'));
}

export function listHrisBidirectionalSyncRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<HrisBidirectionalSyncRunList>(
    apiPath(`/enterprise/federation/hris-sync/runs?${params}`),
  );
}

export function runHrisBidirectionalSync(input: HrisBidirectionalSyncRunInput = {}) {
  return request<HrisBidirectionalSyncRunResult>(apiPath('/enterprise/federation/hris-sync/run'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
