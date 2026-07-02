import { apiPath, request } from './http';

export interface LlmGateStatus {
  feature_enabled: boolean;
  provider_configured: boolean;
  pii_export_allowed: boolean;
  provider: string;
  model: string | null;
  ready: boolean;
  blockers: string[];
}

export async function getLlmStatus(): Promise<LlmGateStatus> {
  return request<LlmGateStatus>(apiPath('/llm/status'));
}
