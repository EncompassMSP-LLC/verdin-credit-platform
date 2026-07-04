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
