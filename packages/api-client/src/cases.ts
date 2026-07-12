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
  CaseLitigationStrength,
  CaseMetro2Findings,
  CaseTradelineChronology,
  Document,
} from './documents';

export type {
  CaseComplianceEvidenceLinks,
  CaseDisputeStrategy,
  CaseFcraFindings,
  CaseLitigationStrength,
  CaseMetro2Findings,
  CaseTradelineChronology,
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

export interface PrepareCreditReportDisputesResult {
  case_id: string;
  prepared: PreparedCreditReportDisputeItem[];
  skipped: string[];
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
  prepared: PreparedCreditReportDisputeItem[];
  skipped: string[];
  note?: string | null;
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
): Promise<CaseComplianceEvidenceLinks> {
  return request<CaseComplianceEvidenceLinks>(
    apiPath(`/cases/${caseId}/compliance-evidence-links`),
  );
}

export async function getCaseLitigationStrength(caseId: string): Promise<CaseLitigationStrength> {
  return request<CaseLitigationStrength>(apiPath(`/cases/${caseId}/litigation-strength`));
}

export async function getCaseDisputeStrategy(caseId: string): Promise<CaseDisputeStrategy> {
  return request<CaseDisputeStrategy>(apiPath(`/cases/${caseId}/dispute-strategy`));
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
