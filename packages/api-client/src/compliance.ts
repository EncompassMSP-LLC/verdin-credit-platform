import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, request, uploadRequest } from './http';

export type ConsentType =
  'croa_services' | 'fcra_dispute' | 'fdcpa_contact' | 'marketing' | 'data_processing';

export type ConsentStatus = 'granted' | 'withdrawn';

export type ConsentSignatureMethod =
  'staff_upload' | 'portal_attestation' | 'portal_signature_image' | 'portal_generated_document';

export type ConsentDocumentTemplateKey =
  'croa_disclosure' | 'croa_service_agreement' | 'fcra_authorization';

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
  document_id: string | null;
  signature_method: ConsentSignatureMethod | null;
  signed_at: string | null;
  signer_name: string | null;
  document_template_key: string | null;
  is_signed: boolean;
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

export interface UploadSignedConsentInput {
  client_id: string;
  case_id: string;
  consent_type: ConsentType;
  file: File;
  signer_name?: string | null;
  notes?: string | null;
  document_template_key?: ConsentDocumentTemplateKey | null;
}

export interface ClientConsentGaps {
  missing_template_keys: ConsentDocumentTemplateKey[];
  missing_template_labels: string[];
  missing_consent_types: ConsentType[];
}

export interface ConsentDocumentTemplate {
  template_key: ConsentDocumentTemplateKey;
  title: string;
  body_text: string;
  merge_field_defaults: Record<string, string> | null;
  legal_review_status: string;
  is_customized: boolean;
  updated_at: string | null;
}

export interface UpdateConsentDocumentTemplateInput {
  title: string;
  body_text: string;
  merge_field_defaults?: Record<string, string> | null;
  legal_review_status?: string;
}

export async function uploadSignedConsentRecord(
  input: UploadSignedConsentInput,
): Promise<ConsentRecord> {
  const form = new FormData();
  form.append('client_id', input.client_id);
  form.append('case_id', input.case_id);
  form.append('consent_type', input.consent_type);
  form.append('file', input.file);
  if (input.signer_name) form.append('signer_name', input.signer_name);
  if (input.notes) form.append('notes', input.notes);
  if (input.document_template_key) {
    form.append('document_template_key', input.document_template_key);
  }
  return uploadRequest<ConsentRecord>(apiPath('/compliance/consents/upload'), form);
}

export async function getClientConsentGaps(clientId: string): Promise<ClientConsentGaps> {
  return request<ClientConsentGaps>(
    `${apiPath('/compliance/consents/gaps')}?client_id=${encodeURIComponent(clientId)}`,
  );
}

export async function listConsentDocumentTemplates(): Promise<ConsentDocumentTemplate[]> {
  return request<ConsentDocumentTemplate[]>(apiPath('/compliance/consent-templates'));
}

export async function updateConsentDocumentTemplate(
  templateKey: ConsentDocumentTemplateKey,
  input: UpdateConsentDocumentTemplateInput,
): Promise<ConsentDocumentTemplate> {
  return request<ConsentDocumentTemplate>(apiPath(`/compliance/consent-templates/${templateKey}`), {
    method: 'PUT',
    body: input,
  });
}

export function getConsentTemplatePreviewUrl(
  templateKey: ConsentDocumentTemplateKey,
  clientId: string,
): string {
  return `${apiPath(`/compliance/consent-templates/${templateKey}/preview`)}?client_id=${encodeURIComponent(clientId)}`;
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
  invocation_reference_id: string | null;
  invocation_channel: string | null;
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

export interface DisputeBureauSubmissionStatus {
  enabled: boolean;
  ready: boolean;
  filing_prep_ready: boolean;
  blockers: string[];
}

export type DisputeBureauSubmissionRunStatus =
  'pending_approval' | 'submitted' | 'rejected' | 'failed';

export interface DisputeBureauSubmissionRun {
  id: string;
  organization_id: string;
  account_id: string;
  case_id: string;
  filing_prep_run_id: string;
  bureau_target: string;
  status: DisputeBureauSubmissionRunStatus;
  submission_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  submitted_at: string | null;
  error_message: string | null;
}

export interface DisputeBureauSubmissionRunResult {
  completed_at: string;
  run: DisputeBureauSubmissionRun;
}

export interface DisputeBureauSubmissionRequest {
  submission_summary: string;
}

export interface ListDisputeBureauSubmissionRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getDisputeBureauSubmissionStatus() {
  return request<DisputeBureauSubmissionStatus>(
    apiPath('/compliance/dispute-bureau-submission/status'),
  );
}

export function listDisputeBureauSubmissionRuns(
  params: ListDisputeBureauSubmissionRunsParams = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<DisputeBureauSubmissionRun>>(
    apiPath(`/compliance/dispute-bureau-submission/runs${query ? `?${query}` : ''}`),
  );
}

export function submitDisputeBureauSubmission(
  filingPrepRunId: string,
  input: DisputeBureauSubmissionRequest,
) {
  return request<DisputeBureauSubmissionRunResult>(
    apiPath(`/compliance/dispute-bureau-submission/prep-runs/${filingPrepRunId}/submit`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveDisputeBureauSubmissionRun(runId: string) {
  return request<DisputeBureauSubmissionRunResult>(
    apiPath(`/compliance/dispute-bureau-submission/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface BureauLiveApiStatus {
  enabled: boolean;
  ready: boolean;
  bureau_submission_ready: boolean;
  blockers: string[];
}

export type BureauLiveApiRunStatus = 'pending_approval' | 'invoked' | 'rejected' | 'failed';

export interface BureauLiveApiRun {
  id: string;
  organization_id: string;
  bureau_submission_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: BureauLiveApiRunStatus;
  invocation_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  invoked_at: string | null;
  error_message: string | null;
}

export interface BureauLiveApiInvokeRequest {
  invocation_summary: string;
}

export interface BureauLiveApiRunResult {
  completed_at: string;
  run: BureauLiveApiRun;
}

export interface ListBureauLiveApiRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getBureauLiveApiStatus() {
  return request<BureauLiveApiStatus>(apiPath('/compliance/bureau-live-api/status'));
}

export function listBureauLiveApiRuns(params: ListBureauLiveApiRunsParams = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<BureauLiveApiRun>>(
    apiPath(`/compliance/bureau-live-api/runs${query ? `?${query}` : ''}`),
  );
}

export function invokeBureauLiveApiFromSubmissionRun(
  bureauSubmissionRunId: string,
  input: BureauLiveApiInvokeRequest,
) {
  return request<BureauLiveApiRunResult>(
    apiPath(`/compliance/bureau-live-api/submission-runs/${bureauSubmissionRunId}/invoke`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveBureauLiveApiRun(runId: string) {
  return request<BureauLiveApiRunResult>(
    apiPath(`/compliance/bureau-live-api/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface AutonomousBureauFilingStatus {
  enabled: boolean;
  ready: boolean;
  bureau_live_api_ready: boolean;
  blockers: string[];
}

export type AutonomousBureauFilingRunStatus = 'pending_approval' | 'filed' | 'rejected' | 'failed';

export interface AutonomousBureauFilingRun {
  id: string;
  organization_id: string;
  bureau_live_api_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: AutonomousBureauFilingRunStatus;
  filing_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  filed_at: string | null;
  error_message: string | null;
}

export interface AutonomousBureauFilingSubmitRequest {
  filing_summary: string;
}

export interface AutonomousBureauFilingRunResult {
  completed_at: string;
  run: AutonomousBureauFilingRun;
}

export interface ListAutonomousBureauFilingRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getAutonomousBureauFilingStatus() {
  return request<AutonomousBureauFilingStatus>(
    apiPath('/compliance/autonomous-bureau-filing/status'),
  );
}

export function listAutonomousBureauFilingRuns(params: ListAutonomousBureauFilingRunsParams = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<AutonomousBureauFilingRun>>(
    apiPath(`/compliance/autonomous-bureau-filing/runs${query ? `?${query}` : ''}`),
  );
}

export function fileAutonomousBureauFilingFromLiveApiRun(
  bureauLiveApiRunId: string,
  input: AutonomousBureauFilingSubmitRequest,
) {
  return request<AutonomousBureauFilingRunResult>(
    apiPath(`/compliance/autonomous-bureau-filing/live-api-runs/${bureauLiveApiRunId}/file`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveAutonomousBureauFilingRun(runId: string) {
  return request<AutonomousBureauFilingRunResult>(
    apiPath(`/compliance/autonomous-bureau-filing/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface FullyAutonomousBureauApiFilingStatus {
  enabled: boolean;
  ready: boolean;
  autonomous_bureau_filing_ready: boolean;
  blockers: string[];
}

export type FullyAutonomousBureauApiFilingRunStatus =
  'pending_approval' | 'executed' | 'rejected' | 'failed';

export interface FullyAutonomousBureauApiFilingRun {
  id: string;
  organization_id: string;
  autonomous_bureau_filing_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: FullyAutonomousBureauApiFilingRunStatus;
  api_filing_summary: string;
  execution_reference_id: string | null;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  executed_at: string | null;
  error_message: string | null;
}

export interface FullyAutonomousBureauApiFilingSubmitRequest {
  api_filing_summary: string;
  execution_reference_id?: string | null;
}

export interface FullyAutonomousBureauApiFilingRunResult {
  completed_at: string;
  run: FullyAutonomousBureauApiFilingRun;
}

export interface ListFullyAutonomousBureauApiFilingRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getFullyAutonomousBureauApiFilingStatus() {
  return request<FullyAutonomousBureauApiFilingStatus>(
    apiPath('/compliance/fully-autonomous-bureau-api-filing/status'),
  );
}

export function listFullyAutonomousBureauApiFilingRuns(
  params: ListFullyAutonomousBureauApiFilingRunsParams = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<FullyAutonomousBureauApiFilingRun>>(
    apiPath(`/compliance/fully-autonomous-bureau-api-filing/runs${query ? `?${query}` : ''}`),
  );
}

export function executeFullyAutonomousBureauApiFilingFromFilingRun(
  autonomousBureauFilingRunId: string,
  input: FullyAutonomousBureauApiFilingSubmitRequest,
) {
  return request<FullyAutonomousBureauApiFilingRunResult>(
    apiPath(
      `/compliance/fully-autonomous-bureau-api-filing/filing-runs/${autonomousBureauFilingRunId}/execute`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveFullyAutonomousBureauApiFilingRun(runId: string) {
  return request<FullyAutonomousBureauApiFilingRunResult>(
    apiPath(`/compliance/fully-autonomous-bureau-api-filing/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface UnsupervisedAutonomousFilingLoopStatus {
  enabled: boolean;
  ready: boolean;
  fully_autonomous_bureau_api_filing_ready: boolean;
  blockers: string[];
}

export type UnsupervisedAutonomousFilingLoopRunStatus =
  'pending_approval' | 'approved' | 'rejected' | 'failed';

export interface UnsupervisedAutonomousFilingLoopRun {
  id: string;
  organization_id: string;
  fully_autonomous_bureau_api_filing_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: UnsupervisedAutonomousFilingLoopRunStatus;
  loop_summary: string;
  loop_reference_id: string | null;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  error_message: string | null;
}

export interface UnsupervisedAutonomousFilingLoopSubmitRequest {
  loop_summary: string;
  loop_reference_id?: string | null;
}

export interface UnsupervisedAutonomousFilingLoopRunResult {
  completed_at: string;
  run: UnsupervisedAutonomousFilingLoopRun;
}

export interface ListUnsupervisedAutonomousFilingLoopRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getUnsupervisedAutonomousFilingLoopStatus() {
  return request<UnsupervisedAutonomousFilingLoopStatus>(
    apiPath('/compliance/unsupervised-autonomous-filing-loops/status'),
  );
}

export function listUnsupervisedAutonomousFilingLoopRuns(
  params: ListUnsupervisedAutonomousFilingLoopRunsParams = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<UnsupervisedAutonomousFilingLoopRun>>(
    apiPath(`/compliance/unsupervised-autonomous-filing-loops/runs${query ? `?${query}` : ''}`),
  );
}

export function startUnsupervisedAutonomousFilingLoopFromApiFilingRun(
  fullyAutonomousBureauApiFilingRunId: string,
  input: UnsupervisedAutonomousFilingLoopSubmitRequest,
) {
  return request<UnsupervisedAutonomousFilingLoopRunResult>(
    apiPath(
      `/compliance/unsupervised-autonomous-filing-loops/api-filing-runs/${fullyAutonomousBureauApiFilingRunId}/start`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveUnsupervisedAutonomousFilingLoopRun(runId: string) {
  return request<UnsupervisedAutonomousFilingLoopRunResult>(
    apiPath(`/compliance/unsupervised-autonomous-filing-loops/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface BureauRefilingStatus {
  enabled: boolean;
  ready: boolean;
  autonomous_filing_ready: boolean;
  blockers: string[];
}

export type BureauRefilingRunStatus = 'pending_approval' | 'refiled' | 'rejected' | 'failed';

export interface BureauRefilingRun {
  id: string;
  organization_id: string;
  autonomous_bureau_filing_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: BureauRefilingRunStatus;
  refiling_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  refiled_at: string | null;
  error_message: string | null;
}

export interface BureauRefilingSubmitRequest {
  refiling_summary: string;
}

export interface BureauRefilingRunResult {
  completed_at: string;
  run: BureauRefilingRun;
}

export interface ListBureauRefilingRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getBureauRefilingStatus() {
  return request<BureauRefilingStatus>(apiPath('/compliance/bureau-refiling/status'));
}

export function listBureauRefilingRuns(params: ListBureauRefilingRunsParams = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<BureauRefilingRun>>(
    apiPath(`/compliance/bureau-refiling/runs${query ? `?${query}` : ''}`),
  );
}

export function refileBureauFromAutonomousFilingRun(
  autonomousBureauFilingRunId: string,
  input: BureauRefilingSubmitRequest,
) {
  return request<BureauRefilingRunResult>(
    apiPath(`/compliance/bureau-refiling/filing-runs/${autonomousBureauFilingRunId}/refile`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveBureauRefilingRun(runId: string) {
  return request<BureauRefilingRunResult>(
    apiPath(`/compliance/bureau-refiling/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface BureauUnsupervisedRefilingStatus {
  enabled: boolean;
  ready: boolean;
  bureau_refiling_ready: boolean;
  blockers: string[];
}

export type BureauUnsupervisedRefilingRunStatus =
  'pending_approval' | 'unsupervised_refiled' | 'rejected' | 'failed';

export interface BureauUnsupervisedRefilingRun {
  id: string;
  organization_id: string;
  bureau_refiling_run_id: string;
  account_id: string;
  case_id: string;
  bureau_target: string;
  status: BureauUnsupervisedRefilingRunStatus;
  refiling_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  timeline_event_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  unsupervised_refiled_at: string | null;
  error_message: string | null;
}

export interface BureauUnsupervisedRefilingSubmitRequest {
  refiling_summary: string;
}

export interface BureauUnsupervisedRefilingRunResult {
  completed_at: string;
  run: BureauUnsupervisedRefilingRun;
}

export interface ListBureauUnsupervisedRefilingRunsParams {
  page?: number;
  page_size?: number;
  account_id?: string;
}

export function getBureauUnsupervisedRefilingStatus() {
  return request<BureauUnsupervisedRefilingStatus>(
    apiPath('/compliance/bureau-unsupervised-refiling/status'),
  );
}

export function listBureauUnsupervisedRefilingRuns(
  params: ListBureauUnsupervisedRefilingRunsParams = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  if (params.account_id) search.set('account_id', params.account_id);
  const query = search.toString();
  return request<PaginatedResponse<BureauUnsupervisedRefilingRun>>(
    apiPath(`/compliance/bureau-unsupervised-refiling/runs${query ? `?${query}` : ''}`),
  );
}

export function startBureauUnsupervisedRefilingFromRefilingRun(
  bureauRefilingRunId: string,
  input: BureauUnsupervisedRefilingSubmitRequest,
) {
  return request<BureauUnsupervisedRefilingRunResult>(
    apiPath(`/compliance/bureau-unsupervised-refiling/refiling-runs/${bureauRefilingRunId}/start`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveBureauUnsupervisedRefilingRun(runId: string) {
  return request<BureauUnsupervisedRefilingRunResult>(
    apiPath(`/compliance/bureau-unsupervised-refiling/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
