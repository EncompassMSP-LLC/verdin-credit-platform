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
