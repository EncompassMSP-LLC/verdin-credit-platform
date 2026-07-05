import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, request } from './http';

export type ConsentType =
  'croa_services' | 'fcra_dispute' | 'fdcpa_contact' | 'marketing' | 'data_processing';

export type ConsentStatus = 'granted' | 'withdrawn';

export type RetentionScope = 'documents' | 'communications' | 'audit_logs' | 'client_profiles';

export type EnforcementTriggerSource = 'manual' | 'scheduled';

export type EnforcementRunStatus = 'completed' | 'failed' | 'skipped';

export interface RetentionEnforcementStatus {
  enabled: boolean;
  active_policy_count: number;
  last_run_at: string | null;
}

export interface RetentionEnforcementRun {
  id: string;
  organization_id: string;
  policy_id: string | null;
  scope: RetentionScope | null;
  trigger_source: EnforcementTriggerSource;
  status: EnforcementRunStatus;
  items_scanned: number;
  items_enforced: number;
  started_at: string;
  completed_at: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface RetentionEnforcementRunResult {
  policies_processed: number;
  items_enforced: number;
  runs: RetentionEnforcementRun[];
}

export interface ListRetentionEnforcementRunsParams {
  page?: number;
  page_size?: number;
}

export interface ComplianceCenterStatus {
  consent_records_enabled: boolean;
  retention_policies_enabled: boolean;
  consent_type_count: number;
  retention_scope_count: number;
  capabilities: string[];
  deferred_capabilities: string[];
}

export interface ConsentRecord {
  id: string;
  organization_id: string;
  client_id: string;
  case_id: string | null;
  consent_type: ConsentType;
  status: ConsentStatus;
  granted_at: string;
  withdrawn_at: string | null;
  source: string;
  notes: string | null;
  created_at: string;
  updated_at: string;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateConsentRecordInput {
  client_id: string;
  case_id?: string | null;
  consent_type: ConsentType;
  source?: string;
  notes?: string | null;
  granted_at?: string | null;
}

export interface ListConsentRecordsParams {
  page?: number;
  page_size?: number;
  client_id?: string;
  case_id?: string;
  consent_type?: ConsentType;
  status?: ConsentStatus;
  sort_by?: 'granted_at' | 'created_at' | 'consent_type' | 'status';
  sort_order?: 'asc' | 'desc';
}

export interface RetentionPolicy {
  id: string;
  organization_id: string;
  name: string;
  scope: RetentionScope;
  retention_days: number;
  is_active: boolean;
  description: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateRetentionPolicyInput {
  name: string;
  scope: RetentionScope;
  retention_days: number;
  is_active?: boolean;
  description?: string | null;
}

export interface UpdateRetentionPolicyInput {
  name?: string;
  retention_days?: number;
  is_active?: boolean;
  description?: string | null;
}

export interface ListRetentionPoliciesParams {
  page?: number;
  page_size?: number;
  scope?: RetentionScope;
  is_active?: boolean;
  sort_by?: 'created_at' | 'name' | 'scope' | 'retention_days';
  sort_order?: 'asc' | 'desc';
}

function buildQuery(params: ListConsentRecordsParams | ListRetentionPoliciesParams): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function getComplianceCenterStatus(): Promise<ComplianceCenterStatus> {
  return request<ComplianceCenterStatus>(apiPath('/compliance/status'));
}

export async function listConsentRecords(
  params: ListConsentRecordsParams = {},
): Promise<PaginatedResponse<ConsentRecord>> {
  return request<PaginatedResponse<ConsentRecord>>(
    `${apiPath('/compliance/consents')}${buildQuery(params)}`,
  );
}

export async function createConsentRecord(input: CreateConsentRecordInput): Promise<ConsentRecord> {
  return request<ConsentRecord>(apiPath('/compliance/consents'), {
    method: 'POST',
    body: input,
  });
}

export async function getConsentRecord(consentId: string): Promise<ConsentRecord> {
  return request<ConsentRecord>(apiPath(`/compliance/consents/${consentId}`));
}

export async function withdrawConsentRecord(consentId: string): Promise<ConsentRecord> {
  return request<ConsentRecord>(apiPath(`/compliance/consents/${consentId}/withdraw`), {
    method: 'POST',
  });
}

export async function listRetentionPolicies(
  params: ListRetentionPoliciesParams = {},
): Promise<PaginatedResponse<RetentionPolicy>> {
  return request<PaginatedResponse<RetentionPolicy>>(
    `${apiPath('/compliance/retention-policies')}${buildQuery(params)}`,
  );
}

export async function createRetentionPolicy(
  input: CreateRetentionPolicyInput,
): Promise<RetentionPolicy> {
  return request<RetentionPolicy>(apiPath('/compliance/retention-policies'), {
    method: 'POST',
    body: input,
  });
}

export async function getRetentionPolicy(policyId: string): Promise<RetentionPolicy> {
  return request<RetentionPolicy>(apiPath(`/compliance/retention-policies/${policyId}`));
}

export async function updateRetentionPolicy(
  policyId: string,
  input: UpdateRetentionPolicyInput,
): Promise<RetentionPolicy> {
  return request<RetentionPolicy>(apiPath(`/compliance/retention-policies/${policyId}`), {
    method: 'PATCH',
    body: input,
  });
}

export async function getRetentionEnforcementStatus(): Promise<RetentionEnforcementStatus> {
  return request<RetentionEnforcementStatus>(apiPath('/compliance/enforcement/status'));
}

export async function listRetentionEnforcementRuns(
  params: ListRetentionEnforcementRunsParams = {},
): Promise<PaginatedResponse<RetentionEnforcementRun>> {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return request<PaginatedResponse<RetentionEnforcementRun>>(
    `${apiPath('/compliance/enforcement/runs')}${query ? `?${query}` : ''}`,
  );
}

export async function runRetentionEnforcement(): Promise<RetentionEnforcementRunResult> {
  return request<RetentionEnforcementRunResult>(apiPath('/compliance/enforcement/run'), {
    method: 'POST',
  });
}

export interface DisputeFilingPrepStatus {
  enabled: boolean;
  ready: boolean;
  agent_execution_ready: boolean;
  blockers: string[];
}

export type DisputeFilingPrepRunStatus = 'pending_approval' | 'prepared' | 'rejected' | 'failed';

export interface DisputeFilingPrepRun {
  id: string;
  organization_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: DisputeFilingPrepRunStatus;
  prep_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  prepared_at: string | null;
  error_message: string | null;
}

export interface DisputeFilingPrepRunResult {
  completed_at: string;
  run: DisputeFilingPrepRun;
}

export interface DisputeFilingPrepRequest {
  prep_summary: string;
  bureau_target?: 'equifax' | 'experian' | 'transunion' | 'innovis';
}

export interface ListDisputeFilingPrepRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getDisputeFilingPrepStatus() {
  return request<DisputeFilingPrepStatus>(apiPath('/compliance/dispute-filing/status'));
}

export function listDisputeFilingPrepRuns(params: ListDisputeFilingPrepRunsParams = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<DisputeFilingPrepRun>>(
    apiPath(`/compliance/dispute-filing/runs${query ? `?${query}` : ''}`),
  );
}

export function submitDisputeFilingPrep(accountId: string, input: DisputeFilingPrepRequest) {
  return request<DisputeFilingPrepRunResult>(
    apiPath(`/compliance/dispute-filing/accounts/${accountId}/prep`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveDisputeFilingPrepRun(runId: string) {
  return request<DisputeFilingPrepRunResult>(
    apiPath(`/compliance/dispute-filing/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
