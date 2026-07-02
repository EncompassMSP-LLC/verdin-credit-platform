import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, request } from './http';

export type ConsentType =
  'croa_services' | 'fcra_dispute' | 'fdcpa_contact' | 'marketing' | 'data_processing';

export type ConsentStatus = 'granted' | 'withdrawn';

export type RetentionScope = 'documents' | 'communications' | 'audit_logs' | 'client_profiles';

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
