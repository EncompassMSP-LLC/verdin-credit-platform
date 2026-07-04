import type { PaginatedResponse } from '@verdin/shared';

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

export interface AgentObservabilityStatus {
  enabled: boolean;
  ready: boolean;
  ai_enabled: boolean;
  blockers: string[];
}

export type AgentObservabilityKind = 'case_review' | 'document_triage' | 'dispute_prep';
export type AgentObservabilityRunStatus = 'pending' | 'running' | 'completed' | 'failed';
export type AgentObservabilityTriggerSource = 'manual' | 'scheduled';

export interface AgentObservabilityRun {
  id: string;
  organization_id: string;
  agent_kind: AgentObservabilityKind;
  trigger_source: AgentObservabilityTriggerSource;
  status: AgentObservabilityRunStatus;
  case_id: string | null;
  steps_completed: number;
  steps_failed: number;
  timeline_event_id: string | null;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface AgentObservabilityRunInput {
  agent_kind?: AgentObservabilityKind;
  case_id?: string | null;
}

export interface AgentObservabilityRunResult {
  completed_at: string;
  run: AgentObservabilityRun;
}

export function getAgentObservabilityStatus() {
  return request<AgentObservabilityStatus>(apiPath('/llm/agents/status'));
}

export function listAgentObservabilityRuns(params: { page?: number; page_size?: number } = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<AgentObservabilityRun>>(
    apiPath(`/llm/agents/runs${query ? `?${query}` : ''}`),
  );
}

export function runAgentObservabilityScaffold(input: AgentObservabilityRunInput = {}) {
  return request<AgentObservabilityRunResult>(apiPath('/llm/agents/run'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
