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

export async function getEnterpriseIdentityStatus(): Promise<EnterpriseIdentityStatus> {
  return request<EnterpriseIdentityStatus>(apiPath('/enterprise/status'));
}
