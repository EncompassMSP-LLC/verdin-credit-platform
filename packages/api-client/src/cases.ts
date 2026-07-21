import type { CasePriority, CaseStage, CaseStatus, PaginatedResponse } from '@verdin/shared';

import {
  apiPath,
  getAccessToken,
  getApiBaseUrl,
  request,
  uploadRequest,
  ApiClientError,
} from './http';
import type {
  CaseComplianceEvidenceLinks,
  CaseDisputeStrategy,
  CaseFcraFindings,
  CaseIdentityTheftFindings,
  CaseLitigationStrength,
  CaseMetro2Findings,
  CaseTradelineChronology,
  ConfirmIdentityTheftAccountRequest,
  DisputeStrategyRun,
  DisputeStrategyRunSummary,
  Document,
  Fcra605bReadinessRun,
  IdentityTheftAccountReview,
  IdentityTheftCaseCenter,
  IdentityTheftProtection,
  UpsertIdentityTheftProtectionRequest,
} from './documents';

export type {
  CaseComplianceEvidenceLinks,
  CaseDisputeStrategy,
  CaseFcraFindings,
  CaseIdentityTheftFindings,
  CaseLitigationStrength,
  CaseMetro2Findings,
  CaseTradelineChronology,
  ConfirmIdentityTheftAccountRequest,
  DisputeStrategyRun,
  DisputeStrategyRunSummary,
  Fcra605bReadinessRun,
  IdentityTheftAccountReview,
  IdentityTheftCaseCenter,
  IdentityTheftProtection,
  UpsertIdentityTheftProtectionRequest,
} from './documents';

export interface Case {
  id: string;
  organization_id: string;
  client_id: string | null;
  case_number: string | null;
  title: string;
  client_name: string;
  client_email: string | null;
  status: CaseStatus;
  stage: CaseStage;
  priority: CasePriority;
  assigned_user_id: string | null;
  summary: string | null;
  notes: string | null;
  opened_at: string;
  closed_at: string | null;
  identity_document_id: string | null;
  proof_of_address_document_id: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateCaseInput {
  title: string;
  client_id?: string | null;
  client_name?: string;
  client_email?: string | null;
  case_number?: string | null;
  status?: CaseStatus;
  stage?: CaseStage;
  priority?: CasePriority;
  assigned_user_id?: string | null;
  summary?: string | null;
  notes?: string | null;
  opened_at?: string | null;
}

export interface UpdateCaseInput {
  title?: string;
  client_id?: string | null;
  client_name?: string;
  client_email?: string | null;
  case_number?: string | null;
  status?: CaseStatus;
  stage?: CaseStage;
  priority?: CasePriority;
  assigned_user_id?: string | null;
  summary?: string | null;
  notes?: string | null;
  opened_at?: string | null;
  closed_at?: string | null;
}

export interface ListCasesParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: CaseStatus;
  stage?: CaseStage;
  priority?: CasePriority;
  assigned_user_id?: string;
  client_id?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

function buildQuery(params: ListCasesParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function createCase(input: CreateCaseInput): Promise<Case> {
  return request<Case>(apiPath('/cases'), { method: 'POST', body: input });
}

export async function listCases(params: ListCasesParams = {}): Promise<PaginatedResponse<Case>> {
  return request<PaginatedResponse<Case>>(`${apiPath('/cases')}${buildQuery(params)}`);
}

export async function getCase(caseId: string): Promise<Case> {
  return request<Case>(apiPath(`/cases/${caseId}`));
}

export async function updateCase(caseId: string, input: UpdateCaseInput): Promise<Case> {
  return request<Case>(apiPath(`/cases/${caseId}`), { method: 'PATCH', body: input });
}

export async function deleteCase(caseId: string): Promise<void> {
  await request<void>(apiPath(`/cases/${caseId}`), { method: 'DELETE' });
}

export async function uploadCaseIdentityDocument(
  caseId: string,
  file: File,
  title?: string,
): Promise<Document> {
  const form = new FormData();
  form.append('file', file);
  if (title) form.append('title', title);
  return uploadRequest<Document>(apiPath(`/cases/${caseId}/identity-document`), form);
}

export interface CaseLlmSummary {
  case_id: string;
  summary: string;
  model: string;
  provider: string;
  prompt_hash: string;
  generated_at: string;
  pii_scrubbed: boolean;
}

export async function generateCaseLlmSummary(caseId: string): Promise<CaseLlmSummary> {
  return request<CaseLlmSummary>(apiPath(`/cases/${caseId}/llm-summary`), { method: 'POST' });
}

export interface BureauTradelineSnapshot {
  bureau: string;
  document_id: string;
  creditor_name: string;
  account_number_masked?: string | null;
  balance?: number | null;
  past_due_amount?: number | null;
  payment_status?: string | null;
  account_status?: string | null;
  account_type?: string | null;
  high_credit?: number | null;
  credit_limit?: number | null;
  open_date?: string | null;
  date_closed?: string | null;
  date_first_delinquency?: string | null;
  date_reported?: string | null;
}

export interface CrossBureauFieldDiff {
  field: string;
  previous?: string | number | null;
  current?: string | number | null;
}

export interface CrossBureauPossibleCause {
  label: string;
  likelihood: 'most_likely' | 'possible' | 'less_likely';
}

export interface CrossBureauDiscrepancy {
  match_key: string;
  creditor_name: string;
  account_number_masked?: string | null;
  discrepancy_types: string[];
  classification: string;
  classification_label: string;
  confidence_score: number;
  workflow_tier: 'none' | 'investigation' | 'dispute';
  bureaus_reporting: string[];
  bureaus_missing: string[];
  bureau_snapshots: BureauTradelineSnapshot[];
  field_diffs?: CrossBureauFieldDiff[];
  possible_causes: CrossBureauPossibleCause[];
  recommended_next_step: string;
  recommended_action: string;
  requires_investigation: boolean;
  dispute_ready: boolean;
  is_actionable: boolean;
}

export interface CrossBureauComparisonSummary {
  total_tradelines: number;
  actionable: number;
  investigation_needed: number;
  dispute_ready: number;
  consistent: number;
  missing_from_bureau: number;
  balance_mismatch: number;
  status_mismatch: number;
  past_due_mismatch?: number;
  dofd_mismatch?: number;
}

export interface CaseCreditReportDiscrepancies {
  case_id: string;
  reports_compared: string[];
  document_ids_by_bureau: Record<string, string>;
  summary: CrossBureauComparisonSummary;
  discrepancies: CrossBureauDiscrepancy[];
}

export interface PrepareCreditReportDisputesInput {
  match_keys?: string[];
  recipient_type?: 'credit_bureau' | 'furnisher';
}

export interface PreparedCreditReportDisputeItem {
  match_key: string;
  account_id: string;
  dispute_letter_id?: string | null;
  created_account: boolean;
  creditor_name: string;
  recommended_action: string;
}

export interface LockedDisputePreparationItem {
  match_key: string;
  creditor_name?: string | null;
  reason: string;
}

export interface PrepareCreditReportDisputesResult {
  case_id: string;
  prepared: PreparedCreditReportDisputeItem[];
  skipped: string[];
  locked?: LockedDisputePreparationItem[];
}

export interface PrepareDisputeStrategyStageInput {
  stage_kind: 'cra_dispute' | 'furnisher_dispute';
  account_keys?: string[];
  recommended_only?: boolean;
}

export interface PrepareDisputeStrategyStageResult {
  case_id: string;
  stage_kind: 'cra_dispute' | 'furnisher_dispute';
  recipient_type: 'credit_bureau' | 'furnisher';
  match_keys: string[];
  direct_account_keys?: string[];
  prepared: PreparedCreditReportDisputeItem[];
  skipped: string[];
  locked?: LockedDisputePreparationItem[];
  note?: string | null;
}

export interface CfpbChecklistSummary {
  accounts_listed: number;
  required_items: number;
  optional_items: number;
  items_present?: number;
  items_missing?: number;
  items_unknown?: number;
}

export type ChecklistCompletionStatus = 'present' | 'missing' | 'unknown';

export type CfpbChecklistCategory = 'correspondence' | 'evidence' | 'chronology' | 'filing';

export interface CfpbChecklistItem {
  item_id: string;
  category: CfpbChecklistCategory;
  title: string;
  detail: string;
  required: boolean;
  completion_status?: ChecklistCompletionStatus;
  completion_source?: 'computed' | 'staff';
  override_note?: string | null;
}

export interface AccountCfpbChecklist {
  account_key: string;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  bureau?: string | null;
  match_key?: string | null;
  top_score: number;
  primary_rule_ids: string[];
  items: CfpbChecklistItem[];
}

export interface CaseCfpbChecklist {
  case_id: string;
  disclaimer: string;
  summary: CfpbChecklistSummary;
  accounts: AccountCfpbChecklist[];
}

export interface AttorneyChecklistSummary {
  accounts_listed: number;
  required_items: number;
  optional_items: number;
  escalation_flagged: number;
  items_present?: number;
  items_missing?: number;
  items_unknown?: number;
}

export type AttorneyChecklistCategory = 'correspondence' | 'evidence' | 'chronology' | 'filing';

export interface AttorneyChecklistItem {
  item_id: string;
  category: AttorneyChecklistCategory;
  title: string;
  detail: string;
  required: boolean;
  completion_status?: ChecklistCompletionStatus;
  completion_source?: 'computed' | 'staff';
  override_note?: string | null;
}

export interface AccountAttorneyChecklist {
  account_key: string;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  bureau?: string | null;
  match_key?: string | null;
  top_score: number;
  primary_rule_ids: string[];
  attorney_escalation: boolean;
  items: AttorneyChecklistItem[];
}

export interface CaseAttorneyChecklist {
  case_id: string;
  disclaimer: string;
  summary: AttorneyChecklistSummary;
  accounts: AccountAttorneyChecklist[];
}

export async function getCaseCreditReportDiscrepancies(
  caseId: string,
): Promise<CaseCreditReportDiscrepancies> {
  return request<CaseCreditReportDiscrepancies>(
    apiPath(`/cases/${caseId}/credit-report-discrepancies`),
  );
}

export async function getCaseMetro2Findings(caseId: string): Promise<CaseMetro2Findings> {
  return request<CaseMetro2Findings>(apiPath(`/cases/${caseId}/metro2-findings`));
}

export async function getCaseFcraFindings(caseId: string): Promise<CaseFcraFindings> {
  return request<CaseFcraFindings>(apiPath(`/cases/${caseId}/fcra-findings`));
}

export async function getCaseIdentityTheftFindings(
  caseId: string,
): Promise<CaseIdentityTheftFindings> {
  return request<CaseIdentityTheftFindings>(apiPath(`/cases/${caseId}/identity-theft-findings`));
}

export async function getCaseIdentityTheftCenter(caseId: string): Promise<IdentityTheftCaseCenter> {
  return request<IdentityTheftCaseCenter>(apiPath(`/cases/${caseId}/identity-theft-center`));
}

export async function confirmIdentityTheftAccount(
  caseId: string,
  body: ConfirmIdentityTheftAccountRequest,
): Promise<IdentityTheftAccountReview> {
  return request<IdentityTheftAccountReview>(
    apiPath(`/cases/${caseId}/identity-theft/account-reviews`),
    { method: 'POST', body },
  );
}

export async function upsertIdentityTheftProtection(
  caseId: string,
  body: UpsertIdentityTheftProtectionRequest,
): Promise<IdentityTheftProtection> {
  return request<IdentityTheftProtection>(apiPath(`/cases/${caseId}/identity-theft/protections`), {
    method: 'PUT',
    body,
  });
}

export async function getCaseTradelineChronology(
  caseId: string,
  params: { bureau?: string } = {},
): Promise<CaseTradelineChronology> {
  const query = new URLSearchParams();
  if (params.bureau) {
    query.set('bureau', params.bureau);
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<CaseTradelineChronology>(
    apiPath(`/cases/${caseId}/tradeline-chronology${suffix}`),
  );
}

export async function getCaseComplianceEvidenceLinks(
  caseId: string,
  params: { include_page_scan?: boolean } = {},
): Promise<CaseComplianceEvidenceLinks> {
  const query = new URLSearchParams();
  if (params.include_page_scan === false) {
    query.set('include_page_scan', 'false');
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<CaseComplianceEvidenceLinks>(
    apiPath(`/cases/${caseId}/compliance-evidence-links${suffix}`),
  );
}

export async function getCaseLitigationStrength(caseId: string): Promise<CaseLitigationStrength> {
  return request<CaseLitigationStrength>(apiPath(`/cases/${caseId}/litigation-strength`));
}

export async function getCaseDisputeStrategy(caseId: string): Promise<CaseDisputeStrategy> {
  return request<CaseDisputeStrategy>(apiPath(`/cases/${caseId}/dispute-strategy`));
}

export async function getLatestCaseDisputeStrategyRun(caseId: string): Promise<DisputeStrategyRun> {
  return request<DisputeStrategyRun>(apiPath(`/cases/${caseId}/dispute-strategy/runs/latest`));
}

export async function listCaseDisputeStrategyRuns(
  caseId: string,
  params: { page?: number; page_size?: number } = {},
): Promise<PaginatedResponse<DisputeStrategyRunSummary>> {
  const query = new URLSearchParams();
  if (params.page !== undefined) {
    query.set('page', String(params.page));
  }
  if (params.page_size !== undefined) {
    query.set('page_size', String(params.page_size));
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<PaginatedResponse<DisputeStrategyRunSummary>>(
    apiPath(`/cases/${caseId}/dispute-strategy/runs${suffix}`),
  );
}

export async function getCaseDisputeStrategyRun(
  caseId: string,
  runId: string,
): Promise<DisputeStrategyRun> {
  return request<DisputeStrategyRun>(apiPath(`/cases/${caseId}/dispute-strategy/runs/${runId}`));
}

export async function getCaseCfpbChecklist(
  caseId: string,
  params: { recommended_only?: boolean } = {},
): Promise<CaseCfpbChecklist> {
  const query = new URLSearchParams();
  if (params.recommended_only === false) {
    query.set('recommended_only', 'false');
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<CaseCfpbChecklist>(
    apiPath(`/cases/${caseId}/dispute-strategy/cfpb-checklist${suffix}`),
  );
}

export async function getCaseAttorneyChecklist(
  caseId: string,
  params: { recommended_only?: boolean } = {},
): Promise<CaseAttorneyChecklist> {
  const query = new URLSearchParams();
  if (params.recommended_only === false) {
    query.set('recommended_only', 'false');
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return request<CaseAttorneyChecklist>(
    apiPath(`/cases/${caseId}/dispute-strategy/attorney-checklist${suffix}`),
  );
}

export async function prepareCaseDisputeStrategyStage(
  caseId: string,
  input: PrepareDisputeStrategyStageInput,
): Promise<PrepareDisputeStrategyStageResult> {
  return request<PrepareDisputeStrategyStageResult>(
    apiPath(`/cases/${caseId}/dispute-strategy/prepare`),
    { method: 'POST', body: input },
  );
}

export async function prepareCaseCreditReportDisputes(
  caseId: string,
  input: PrepareCreditReportDisputesInput = {},
): Promise<PrepareCreditReportDisputesResult> {
  return request<PrepareCreditReportDisputesResult>(
    apiPath(`/cases/${caseId}/credit-report-discrepancies/prepare-disputes`),
    { method: 'POST', body: input },
  );
}

export interface CaseCreditReportReparseQueuedItem {
  document_id: string;
  job_id: string;
  job_type: string;
}

export interface CaseCreditReportReparseSkippedItem {
  document_id: string;
  reason: string;
}

export interface CaseCreditReportBulkReparse {
  case_id: string;
  queued_count: number;
  skipped_count: number;
  queued: CaseCreditReportReparseQueuedItem[];
  skipped: CaseCreditReportReparseSkippedItem[];
}

export async function bulkReparseCaseCreditReports(
  caseId: string,
): Promise<CaseCreditReportBulkReparse> {
  return request<CaseCreditReportBulkReparse>(
    apiPath(`/cases/${caseId}/parsed-credit-reports/reparse`),
    { method: 'POST' },
  );
}

export interface CaseMetadataReextractQueuedItem {
  document_id: string;
  job_id: string;
  job_type: string;
}

export interface CaseMetadataReextractSkippedItem {
  document_id: string;
  reason: string;
}

export interface CaseMetadataBulkReextract {
  case_id: string;
  queued_count: number;
  skipped_count: number;
  queued: CaseMetadataReextractQueuedItem[];
  skipped: CaseMetadataReextractSkippedItem[];
}

export async function bulkReextractCaseMetadata(
  caseId: string,
): Promise<CaseMetadataBulkReextract> {
  return request<CaseMetadataBulkReextract>(apiPath(`/cases/${caseId}/metadata/reextract`), {
    method: 'POST',
  });
}

function parseContentDispositionFilename(header: string | null, fallback: string): string {
  if (!header) return fallback;
  const match = /filename="([^"]+)"/.exec(header);
  return match?.[1] ?? fallback;
}

export async function downloadCaseDisputeMailPackets(
  caseId: string,
): Promise<{ blob: Blob; filename: string }> {
  const url = `${getApiBaseUrl()}${apiPath(`/cases/${caseId}/dispute-mail-packets/export`)}`;
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as { detail?: string; code?: string };
    throw new ApiClientError(
      error.detail || `HTTP ${response.status}`,
      response.status,
      error.code,
    );
  }

  const filename = parseContentDispositionFilename(
    response.headers.get('content-disposition'),
    `case-mail-packets-${caseId.slice(0, 8)}.zip`,
  );
  const blob = await response.blob();
  return { blob, filename };
}

export async function downloadCaseDisputeReportExcerpts(
  caseId: string,
): Promise<{ blob: Blob; filename: string }> {
  const url = `${getApiBaseUrl()}${apiPath(`/cases/${caseId}/dispute-report-excerpts/export`)}`;
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as { detail?: string; code?: string };
    throw new ApiClientError(
      error.detail || `HTTP ${response.status}`,
      response.status,
      error.code,
    );
  }

  const filename = parseContentDispositionFilename(
    response.headers.get('content-disposition'),
    `case-report-excerpts-${caseId.slice(0, 8)}.zip`,
  );
  const blob = await response.blob();
  return { blob, filename };
}

async function downloadChecklistExport(
  caseId: string,
  path: string,
  fallbackFilename: string,
  params: {
    recommended_only?: boolean;
    include_letters?: boolean;
    letter_format?: 'text' | 'pdf';
    include_mail_packets?: boolean;
    include_report_excerpts?: boolean;
    format?: 'md' | 'pdf';
    document_ids?: string[];
  } = {},
): Promise<{ blob: Blob; filename: string }> {
  const query = new URLSearchParams();
  if (params.recommended_only === false) {
    query.set('recommended_only', 'false');
  }
  for (const documentId of params.document_ids ?? []) {
    query.append('document_id', documentId);
  }
  if (params.include_letters === false) {
    query.set('include_letters', 'false');
  }
  if (params.letter_format === 'pdf') {
    query.set('letter_format', 'pdf');
  }
  if (params.include_mail_packets === true) {
    query.set('include_mail_packets', 'true');
  }
  if (params.include_report_excerpts === true) {
    query.set('include_report_excerpts', 'true');
  }
  if (params.format === 'pdf') {
    query.set('format', 'pdf');
  }
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const url = `${getApiBaseUrl()}${apiPath(`${path}${suffix}`)}`;
  const headers: Record<string, string> = {};
  const token = getAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, { headers });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as { detail?: string | { message?: string }; code?: string };
    const detail =
      typeof error.detail === 'string'
        ? error.detail
        : error.detail?.message || `HTTP ${response.status}`;
    throw new ApiClientError(detail, response.status, error.code);
  }

  const filename = parseContentDispositionFilename(
    response.headers.get('content-disposition'),
    fallbackFilename,
  );
  const blob = await response.blob();
  return { blob, filename };
}

export async function downloadCaseCfpbChecklist(
  caseId: string,
  params: { recommended_only?: boolean; format?: 'md' | 'pdf' } = {},
): Promise<{ blob: Blob; filename: string }> {
  const extension = params.format === 'pdf' ? 'pdf' : 'md';
  return downloadChecklistExport(
    caseId,
    `/cases/${caseId}/dispute-strategy/cfpb-checklist/export`,
    `cfpb-checklist-${caseId.slice(0, 8)}.${extension}`,
    params,
  );
}

export async function downloadCaseAttorneyChecklist(
  caseId: string,
  params: { recommended_only?: boolean; format?: 'md' | 'pdf' } = {},
): Promise<{ blob: Blob; filename: string }> {
  const extension = params.format === 'pdf' ? 'pdf' : 'md';
  return downloadChecklistExport(
    caseId,
    `/cases/${caseId}/dispute-strategy/attorney-checklist/export`,
    `attorney-checklist-${caseId.slice(0, 8)}.${extension}`,
    params,
  );
}

export async function downloadCaseCfpbChecklistPacket(
  caseId: string,
  params: {
    recommended_only?: boolean;
    include_letters?: boolean;
    letter_format?: 'text' | 'pdf';
    include_mail_packets?: boolean;
    include_report_excerpts?: boolean;
  } = {},
): Promise<{ blob: Blob; filename: string }> {
  return downloadChecklistExport(
    caseId,
    `/cases/${caseId}/dispute-strategy/cfpb-checklist/packet.zip`,
    `cfpb-checklist-packet-${caseId.slice(0, 8)}.zip`,
    params,
  );
}

export async function downloadCaseAttorneyChecklistPacket(
  caseId: string,
  params: {
    recommended_only?: boolean;
    include_letters?: boolean;
    letter_format?: 'text' | 'pdf';
    include_mail_packets?: boolean;
    include_report_excerpts?: boolean;
  } = {},
): Promise<{ blob: Blob; filename: string }> {
  return downloadChecklistExport(
    caseId,
    `/cases/${caseId}/dispute-strategy/attorney-checklist/packet.zip`,
    `attorney-checklist-packet-${caseId.slice(0, 8)}.zip`,
    params,
  );
}

export async function downloadCaseIdentityTheft605bPacket(
  caseId: string,
  params: { letter_format?: 'text' | 'pdf'; document_ids?: string[] } = {},
): Promise<{ blob: Blob; filename: string }> {
  return downloadChecklistExport(
    caseId,
    `/cases/${caseId}/identity-theft/605b-packet.zip`,
    `fcra-605b-block-packet-${caseId.slice(0, 8)}.zip`,
    { letter_format: params.letter_format ?? 'pdf', document_ids: params.document_ids },
  );
}

export async function runCaseIdentityTheft605bReadinessAudit(
  caseId: string,
): Promise<Fcra605bReadinessRun> {
  return request<Fcra605bReadinessRun>(
    apiPath(`/cases/${caseId}/identity-theft/605b-readiness-runs`),
    { method: 'POST' },
  );
}

export async function getLatestCaseIdentityTheft605bReadinessRun(
  caseId: string,
): Promise<Fcra605bReadinessRun> {
  return request<Fcra605bReadinessRun>(
    apiPath(`/cases/${caseId}/identity-theft/605b-readiness-runs/latest`),
  );
}

export interface UpsertChecklistOverrideInput {
  checklist_kind: 'cfpb' | 'attorney';
  account_key: string;
  item_id: string;
  completion_status?: ChecklistCompletionStatus | null;
  note?: string | null;
}

export async function upsertCaseChecklistOverride(
  caseId: string,
  input: UpsertChecklistOverrideInput,
): Promise<CaseCfpbChecklist | CaseAttorneyChecklist> {
  return request<CaseCfpbChecklist | CaseAttorneyChecklist>(
    apiPath(`/cases/${caseId}/dispute-strategy/checklist-overrides`),
    { method: 'PUT', body: input },
  );
}
