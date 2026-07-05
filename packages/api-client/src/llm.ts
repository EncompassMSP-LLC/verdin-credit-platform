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

export interface AgentExecutionStatus {
  enabled: boolean;
  ready: boolean;
  observability_ready: boolean;
  blockers: string[];
}

export type AgentExecutionStepStatus = 'pending_approval' | 'executed' | 'rejected' | 'failed';

export interface AgentExecutionStep {
  id: string;
  organization_id: string;
  agent_kind: AgentObservabilityKind;
  status: AgentExecutionStepStatus;
  case_id: string | null;
  step_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  executed_at: string | null;
  error_message: string | null;
}

export interface AgentExecutionStepSubmitInput {
  agent_kind?: AgentObservabilityKind;
  step_summary: string;
  case_id?: string | null;
}

export interface AgentExecutionStepResult {
  completed_at: string;
  step: AgentExecutionStep;
}

export function getAgentExecutionStatus() {
  return request<AgentExecutionStatus>(apiPath('/llm/execution/status'));
}

export function listAgentExecutionSteps(params: { page?: number; page_size?: number } = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<AgentExecutionStep>>(
    apiPath(`/llm/execution/steps${query ? `?${query}` : ''}`),
  );
}

export function submitAgentExecutionStep(input: AgentExecutionStepSubmitInput) {
  return request<AgentExecutionStepResult>(apiPath('/llm/execution/steps'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function approveAgentExecutionStep(stepId: string) {
  return request<AgentExecutionStepResult>(apiPath(`/llm/execution/steps/${stepId}/approve`), {
    method: 'POST',
  });
}

export type AgentExternalToolKind = 'web_lookup' | 'document_fetch' | 'crm_update';
export type AgentToolInvocationStatus = 'pending_approval' | 'invoked' | 'rejected' | 'failed';

export interface AgentExternalToolCallingStatus {
  enabled: boolean;
  ready: boolean;
  agent_execution_ready: boolean;
  blockers: string[];
}

export interface AgentToolInvocationRequest {
  id: string;
  organization_id: string;
  tool_kind: AgentExternalToolKind;
  status: AgentToolInvocationStatus;
  case_id: string | null;
  invocation_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  invoked_at: string | null;
  error_message: string | null;
}

export interface AgentToolInvocationSubmitInput {
  tool_kind?: AgentExternalToolKind;
  invocation_summary: string;
  case_id?: string | null;
}

export interface AgentToolInvocationRequestResult {
  completed_at: string;
  request: AgentToolInvocationRequest;
}

export function getAgentExternalToolCallingStatus() {
  return request<AgentExternalToolCallingStatus>(apiPath('/llm/tool-calling/status'));
}

export function listAgentToolInvocationRequests(
  params: { page?: number; page_size?: number; case_id?: string } = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.case_id) search.set('case_id', params.case_id);
  const query = search.toString();
  return request<PaginatedResponse<AgentToolInvocationRequest>>(
    apiPath(`/llm/tool-calling/requests${query ? `?${query}` : ''}`),
  );
}

export function submitAgentToolInvocationRequest(input: AgentToolInvocationSubmitInput) {
  return request<AgentToolInvocationRequestResult>(apiPath('/llm/tool-calling/requests'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function approveAgentToolInvocationRequest(requestId: string) {
  return request<AgentToolInvocationRequestResult>(
    apiPath(`/llm/tool-calling/requests/${requestId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface LlmDisputeDraftAugmentStatus {
  enabled: boolean;
  ready: boolean;
  llm_ready: boolean;
  blockers: string[];
}

export function getLlmDisputeDraftAugmentStatus() {
  return request<LlmDisputeDraftAugmentStatus>(apiPath('/llm/dispute-draft/status'));
}
