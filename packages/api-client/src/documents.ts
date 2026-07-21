import type {
  DocumentType,
  DocumentProcessingStatus,
  ExtractionMethod,
  MatchedEntityType,
  MetadataStatus,
  PaginatedResponse,
  ResolutionMethod,
  ResolutionStatus,
} from '@verdin/shared';

import { apiPath, getApiBaseUrl, request, uploadRequest } from './http';
import type { Task } from './tasks';

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  file_hash: string;
  created_at: string;
  created_by_id: string | null;
}

export interface Document {
  id: string;
  organization_id: string;
  case_id: string;
  account_id: string | null;
  title: string;
  description: string | null;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  file_hash: string;
  version_number: number;
  is_duplicate: boolean;
  duplicate_of_id: string | null;
  processing_status: DocumentProcessingStatus;
  ocr_processed_at: string | null;
  ocr_version_number: number | null;
  document_type: DocumentType | null;
  confidence_score: number | null;
  classified_at: string | null;
  metadata_status?: MetadataStatus | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
  versions?: DocumentVersion[];
}

export interface UploadDocumentInput {
  file: File;
  title: string;
  case_id: string;
  description?: string | null;
  account_id?: string | null;
}

export interface UpdateDocumentInput {
  title?: string;
  description?: string | null;
  account_id?: string | null;
}

export interface ListDocumentsParams {
  page?: number;
  page_size?: number;
  search?: string;
  case_id?: string;
  account_id?: string;
  is_duplicate?: boolean;
  processing_status?: DocumentProcessingStatus;
  metadata_status?: MetadataStatus;
  resolution_status?: ResolutionStatus;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface DocumentOcrResult {
  document_id: string;
  processing_status: DocumentProcessingStatus;
  ocr_text: string | null;
  ocr_error: string | null;
  ocr_processed_at: string | null;
  ocr_version_number: number | null;
}

export interface DocumentDuplicateGroup {
  document_id: string;
  canonical_document: Document;
  duplicate_documents: Document[];
  duplicate_count: number;
}

export interface DocumentMetadata {
  document_id: string;
  consumer_name: string | null;
  bureau: string | null;
  creditor: string | null;
  collection_agency: string | null;
  account_number_masked: string | null;
  report_date: string | null;
  open_date: string | null;
  balance: number | null;
  payment_status: string | null;
  addresses: string[];
  phone_numbers: string[];
  ssn_masked: string | null;
  confidence_score: number | null;
  extraction_method: ExtractionMethod;
  metadata_status: MetadataStatus;
  extracted_at: string | null;
  extraction_error: string | null;
}

export interface DocumentParsedCreditReport {
  document_id: string;
  schema_version: string;
  bureau: string;
  parser_name: string;
  parser_confidence: number;
  parsed_report: Record<string, unknown>;
  is_partial: boolean;
  warnings: string[];
  parsed_at: string;
}

export interface ParsedReportFieldDiff {
  field: string;
  previous?: string | number | null;
  current?: string | number | null;
}

export interface Metro2FindingSummary {
  total: number;
  high: number;
  medium: number;
  low: number;
  tradelines_evaluated: number;
}

export interface Metro2Finding {
  rule_id: string;
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  tradeline_index: number;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  fields: string[];
  observed: Record<string, unknown>;
}

export interface DocumentMetro2Findings {
  document_id: string;
  bureau: string;
  schema_version?: string | null;
  summary: Metro2FindingSummary;
  findings: Metro2Finding[];
}

export interface CaseMetro2Findings {
  case_id: string;
  reports_evaluated: string[];
  document_ids_by_bureau: Record<string, string>;
  summary: Metro2FindingSummary;
  documents: DocumentMetro2Findings[];
}

export interface FcraFindingSummary {
  total: number;
  high: number;
  medium: number;
  low: number;
  tradelines_evaluated: number;
}

export interface FcraFinding {
  rule_id: string;
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  fcra_sections: string[];
  tradeline_index: number;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  fields: string[];
  observed: Record<string, unknown>;
}

export interface DocumentFcraFindings {
  document_id: string;
  bureau: string;
  schema_version?: string | null;
  as_of_date?: string | null;
  summary: FcraFindingSummary;
  findings: FcraFinding[];
}

export interface CaseFcraFindings {
  case_id: string;
  reports_evaluated: string[];
  document_ids_by_bureau: Record<string, string>;
  summary: FcraFindingSummary;
  documents: DocumentFcraFindings[];
}

export type IdentityTheftConfirmation =
  | 'recognize'
  | 'need_more_info'
  | 'inaccurate_reporting'
  | 'identity_theft'
  | 'mixed_file'
  | 'authorized_user'
  | 'unsure';

export interface IdentityTheftFindingSummary {
  total: number;
  high: number;
  medium: number;
  low: number;
  tradelines_evaluated: number;
  report_level_indicators: number;
  tradeline_indicators: number;
  personal_info_indicators: number;
  ordinary_dispute_locked_count: number;
}

export interface IdentityTheftFinding {
  rule_id: string;
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  detection_source:
    'REPORT_TEXT' | 'TRADELINE_HEURISTIC' | 'CONSUMER_CONFIRMATION' | 'PERSONAL_INFO';
  issue_type: 'IDENTITY_THEFT_INDICATOR' | 'CONFIRMED_IDENTITY_THEFT_CLAIM';
  confidence: number;
  consumer_confirmed: boolean;
  legal_path?: 'FCRA_605B' | null;
  ordinary_dispute_locked: boolean;
  required_action:
    'CONSUMER_REVIEW' | 'OPEN_IDENTITY_THEFT_CASE' | 'PREPARE_605B' | 'CONTINUE_ORDINARY_DISPUTE';
  classification: Record<string, unknown>;
  tradeline_index?: number | null;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  fields: string[];
  observed: Record<string, unknown>;
}

export interface DocumentIdentityTheftFindings {
  document_id: string;
  bureau: string;
  schema_version?: string | null;
  as_of_date?: string | null;
  banner_active: boolean;
  banner_title?: string | null;
  banner_body?: string | null;
  ordinary_dispute_locked: boolean;
  summary: IdentityTheftFindingSummary;
  findings: IdentityTheftFinding[];
  protections_detected: Record<string, unknown>[];
}

export interface CaseIdentityTheftFindings {
  case_id: string;
  reports_evaluated: string[];
  document_ids_by_bureau: Record<string, string>;
  banner_active: boolean;
  banner_title?: string | null;
  banner_body?: string | null;
  ordinary_dispute_locked: boolean;
  summary: IdentityTheftFindingSummary;
  documents: DocumentIdentityTheftFindings[];
}

export interface Fcra605bItem {
  item_id: string;
  label: string;
  required: boolean;
  status: 'present' | 'missing' | 'unknown';
}

export interface Fcra605bReadiness {
  remedy_type: string;
  not_ordinary_dispute: boolean;
  packet_readiness: number;
  items: Fcra605bItem[];
  missing_evidence: string[];
}

export interface Fcra605bReadinessRun {
  id: string;
  case_id: string;
  generated_at: string;
  generated_by_id?: string | null;
  is_ready: boolean;
  packet_readiness?: number | null;
  confirmed_count: number;
  attestation_recorded: boolean;
  bureaus: string[];
  missing_evidence: string[];
  blocking_reasons: string[];
}

export interface IdentityTheftIncident {
  id: string;
  case_id: string;
  status: 'open' | 'in_recovery' | 'closed';
  discovered_at?: string | null;
  suspected_theft_period_start?: string | null;
  suspected_theft_period_end?: string | null;
  unrecognized_addresses: unknown[];
  unrecognized_aliases: unknown[];
  companies_contacted: unknown[];
  police_report_number?: string | null;
  police_report_agency?: string | null;
  police_report_filed_at?: string | null;
  ftc_report_status: string;
  ftc_report_reference?: string | null;
  evidence_checklist: unknown[];
  recovery_step: number;
  consumer_attestation_at?: string | null;
  consumer_attestation_text?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IdentityTheftAccountReview {
  id: string;
  case_id: string;
  incident_id?: string | null;
  account_id?: string | null;
  document_id?: string | null;
  bureau?: string | null;
  tradeline_index?: number | null;
  match_key?: string | null;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  detection_source: string;
  rule_id?: string | null;
  confidence: number;
  issue_type: 'IDENTITY_THEFT_INDICATOR' | 'CONFIRMED_IDENTITY_THEFT_CLAIM';
  consumer_confirmation?: IdentityTheftConfirmation | null;
  consumer_confirmed_at?: string | null;
  ordinary_dispute_locked: boolean;
  legal_path?: string | null;
  packet_readiness?: number | null;
  missing_evidence: unknown[];
  attestation_accepted: boolean;
  classification: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface IdentityTheftProtection {
  id: string;
  case_id: string;
  protection_type:
    | 'initial_fraud_alert'
    | 'extended_fraud_alert'
    | 'active_duty_alert'
    | 'equifax_freeze'
    | 'experian_freeze'
    | 'transunion_freeze';
  status: 'active' | 'inactive' | 'frozen' | 'unfrozen' | 'unknown';
  placed_at?: string | null;
  expires_at?: string | null;
  source: string;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface IdentityTheftCaseCenter {
  case_id: string;
  disclaimer: string;
  confirmation_options: string[];
  attestation_text: string;
  recovery_workflow_steps: { step: string; title: string }[];
  default_evidence_checklist: { item_id: string; label: string }[];
  banner_active: boolean;
  banner_title?: string | null;
  banner_body?: string | null;
  findings?: CaseIdentityTheftFindings | null;
  incident?: IdentityTheftIncident | null;
  account_reviews: IdentityTheftAccountReview[];
  protections: IdentityTheftProtection[];
  fcra_605b?: Fcra605bReadiness | null;
}

export interface ConfirmIdentityTheftAccountRequest {
  confirmation: IdentityTheftConfirmation;
  attestation_accepted?: boolean;
  account_id?: string | null;
  document_id?: string | null;
  bureau?: string | null;
  tradeline_index?: number | null;
  match_key?: string | null;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  detection_source?:
    'REPORT_TEXT' | 'TRADELINE_HEURISTIC' | 'CONSUMER_CONFIRMATION' | 'PERSONAL_INFO';
  rule_id?: string | null;
  confidence?: number;
  discovered_at?: string | null;
}

export interface UpsertIdentityTheftProtectionRequest {
  protection_type: IdentityTheftProtection['protection_type'];
  status: IdentityTheftProtection['status'];
  placed_at?: string | null;
  expires_at?: string | null;
  notes?: string | null;
}

export interface TradelineChronologySummary {
  tradelines: number;
  with_changes: number;
  snapshots: number;
  events: number;
  reports_evaluated: number;
}

export interface TradelineChronologySnapshot {
  document_id: string;
  parsed_at: string;
  as_of_date?: string | null;
  present: boolean;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  balance?: number | null;
  past_due_amount?: number | null;
  account_status?: string | null;
  payment_status?: string | null;
  date_first_delinquency?: string | null;
  date_closed?: string | null;
  remarks?: string | null;
  high_credit?: number | null;
  credit_limit?: number | null;
}

export type TradelineChronologyEventType =
  | 'appeared'
  | 'disappeared'
  | 'balance_increased'
  | 'balance_decreased'
  | 'past_due_changed'
  | 'status_changed'
  | 'dofd_changed'
  | 'date_closed_changed'
  | 'field_changed';

export interface TradelineChronologyEvent {
  event_type: TradelineChronologyEventType;
  severity: 'low' | 'medium' | 'high';
  field?: string | null;
  from_document_id?: string | null;
  to_document_id: string;
  from_parsed_at?: string | null;
  to_parsed_at: string;
  previous?: string | number | null;
  current?: string | number | null;
  summary: string;
}

export interface TradelineChronologyItem {
  match_key: string;
  bureau: string;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  snapshot_count: number;
  event_count: number;
  snapshots: TradelineChronologySnapshot[];
  events: TradelineChronologyEvent[];
}

export interface CaseTradelineChronology {
  case_id: string;
  reports_evaluated: number;
  bureaus: string[];
  summary: TradelineChronologySummary;
  tradelines: TradelineChronologyItem[];
}

export interface ComplianceEvidenceSummary {
  findings_linked: number;
  with_pages: number;
  missing_pages: number;
  exhibits_available: number;
  report_links: number;
}

export interface ComplianceEvidenceReportLink {
  document_id: string;
  bureau?: string | null;
  download_path: string;
  page_numbers?: number[] | null;
  page_confidence: 'matched' | 'unavailable' | 'deferred';
  excerpt_available: boolean;
}

export interface ComplianceEvidenceExhibitLink {
  document_id: string;
  document_type: string;
  role: 'identity' | 'proof_of_address' | 'supporting' | 'suggested';
  label: string;
}

export interface ComplianceEvidenceLinkItem {
  source_kind: 'metro2' | 'fcra';
  source_id: string;
  rule_id: string;
  severity: string;
  title: string;
  bureau?: string | null;
  tradeline_index?: number | null;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  report_links: ComplianceEvidenceReportLink[];
  exhibit_links: ComplianceEvidenceExhibitLink[];
  checklist_hints: string[];
}

export interface CaseComplianceEvidenceLinks {
  case_id: string;
  summary: ComplianceEvidenceSummary;
  items: ComplianceEvidenceLinkItem[];
}

export interface LitigationStrengthSummary {
  issues_scored: number;
  high_priority: number;
  medium_priority: number;
  low_priority: number;
  top_score: number;
  average_score: number;
}

export interface LitigationStrengthIssue {
  source_kind: 'metro2' | 'fcra' | 'cross_bureau' | 'chronology' | 'identity_theft';
  source_id: string;
  rule_id: string;
  score: number;
  rank: number;
  title: string;
  rationale: string;
  severity: string;
  bureau?: string | null;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  match_key?: string | null;
  factors: string[];
}

export interface CaseLitigationStrength {
  case_id: string;
  summary: LitigationStrengthSummary;
  issues: LitigationStrengthIssue[];
}

export interface DisputeStrategySummary {
  accounts_planned: number;
  issues_covered: number;
  high_strength_accounts: number;
  cfpb_recommended: number;
  attorney_recommended: number;
}

export type DisputeStrategyStageKind =
  'cra_dispute' | 'furnisher_dispute' | 'cfpb_escalation' | 'attorney_preserve';

export interface DisputeStrategyStage {
  stage_order: number;
  stage_kind: DisputeStrategyStageKind;
  title: string;
  objective: string;
  rationale: string;
  issue_source_ids: string[];
  evidence_hints: string[];
  recommended: boolean;
}

export interface AccountDisputeStrategy {
  account_key: string;
  creditor_name?: string | null;
  account_number_masked?: string | null;
  bureau?: string | null;
  match_key?: string | null;
  top_score: number;
  issue_count: number;
  primary_rule_ids: string[];
  summary: string;
  stages: DisputeStrategyStage[];
}

export interface CaseDisputeStrategy {
  case_id: string;
  disclaimer: string;
  summary: DisputeStrategySummary;
  strategies: AccountDisputeStrategy[];
  run_id?: string | null;
  generated_at?: string | null;
}

export interface DisputeStrategyRun {
  id: string;
  case_id: string;
  generated_at: string;
  generated_by_id?: string | null;
  disclaimer: string;
  summary: DisputeStrategySummary;
  strategies: AccountDisputeStrategy[];
  accounts_planned: number;
  issues_covered: number;
}

export interface DisputeStrategyRunSummary {
  id: string;
  case_id: string;
  generated_at: string;
  generated_by_id?: string | null;
  accounts_planned: number;
  issues_covered: number;
  high_strength_accounts: number;
  cfpb_recommended: number;
  attorney_recommended: number;
}

export interface ParsedReportAccountChange {
  match_key: string;
  creditor_name: string | null;
  account_number_masked: string | null;
  change_type: 'added' | 'removed' | 'changed' | 'unchanged';
  previous_balance: number | null;
  current_balance: number | null;
  balance_delta: number | null;
  previous_payment_status: string | null;
  current_payment_status: string | null;
  field_diffs?: ParsedReportFieldDiff[];
}

export interface ParsedReportComparisonSummary {
  added: number;
  removed: number;
  changed: number;
  unchanged: number;
}

export interface DocumentParsedCreditReportComparison {
  document_id: string;
  bureau: string;
  previous_document_id: string | null;
  current_parsed_at: string;
  previous_parsed_at: string | null;
  summary: ParsedReportComparisonSummary;
  account_changes: ParsedReportAccountChange[];
}

export interface ParsedReportAccountCandidate {
  source_index: number;
  case_id: string;
  bureau: string;
  creditor_name: string;
  original_creditor: string | null;
  account_number_masked: string | null;
  account_type: string;
  account_status: string;
  payment_status: string;
  balance: string | null;
  past_due_amount: string | null;
  high_balance?: string | null;
  credit_limit?: string | null;
  date_opened?: string | null;
  date_reported?: string | null;
  date_first_delinquency?: string | null;
  remarks: string | null;
  payment_history?: string | null;
  date_closed?: string | null;
}

export interface DocumentParsedCreditReportAccountCandidates {
  document_id: string;
  bureau: string;
  candidates: ParsedReportAccountCandidate[];
}

export interface ImportParsedReportAccountsRequest {
  source_indices?: number[];
  skip_existing?: boolean;
}

export interface ImportedParsedReportAccountItem {
  source_index: number;
  account_id: string;
  created: boolean;
  creditor_name: string;
}

export interface ImportParsedReportAccountsResponse {
  document_id: string;
  case_id: string;
  imported: ImportedParsedReportAccountItem[];
  skipped_indices: number[];
}

export interface DocumentEntityResolution {
  id: string;
  document_id: string;
  entity_type: MatchedEntityType;
  matched_entity_id: string | null;
  confidence_score: number;
  resolution_status: ResolutionStatus;
  resolution_method: ResolutionMethod;
  reasoning: string | null;
  candidate_entity_ids: string[];
  reviewed_at: string | null;
  reviewed_by_id: string | null;
}

export interface DocumentResolutions {
  document_id: string;
  resolutions: DocumentEntityResolution[];
}

function buildQuery(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function uploadDocument(input: UploadDocumentInput): Promise<Document> {
  const form = new FormData();
  form.append('file', input.file);
  form.append('title', input.title);
  form.append('case_id', input.case_id);
  if (input.description) form.append('description', input.description);
  if (input.account_id) form.append('account_id', input.account_id);
  return uploadRequest<Document>(apiPath('/documents'), form);
}

export async function listDocuments(
  params: ListDocumentsParams = {},
): Promise<PaginatedResponse<Document>> {
  return request<PaginatedResponse<Document>>(
    `${apiPath('/documents')}${buildQuery(params as Record<string, unknown>)}`,
  );
}

export async function getDocument(documentId: string): Promise<Document> {
  return request<Document>(apiPath(`/documents/${documentId}`));
}

export async function getDocumentDuplicateGroup(
  documentId: string,
): Promise<DocumentDuplicateGroup> {
  return request<DocumentDuplicateGroup>(apiPath(`/documents/${documentId}/duplicates`));
}

export async function updateDocument(
  documentId: string,
  input: UpdateDocumentInput,
): Promise<Document> {
  return request<Document>(apiPath(`/documents/${documentId}`), { method: 'PATCH', body: input });
}

export async function deleteDocument(documentId: string): Promise<void> {
  await request<void>(apiPath(`/documents/${documentId}`), { method: 'DELETE' });
}

export async function uploadDocumentVersion(documentId: string, file: File): Promise<Document> {
  const form = new FormData();
  form.append('file', file);
  return uploadRequest<Document>(apiPath(`/documents/${documentId}/versions`), form);
}

export function getDocumentDownloadUrl(documentId: string, version?: number): string {
  const base = `${getApiBaseUrl()}${apiPath(`/documents/${documentId}/download`)}`;
  return version ? `${base}?version=${version}` : base;
}

export async function listDocumentVersions(documentId: string): Promise<DocumentVersion[]> {
  return request<DocumentVersion[]>(apiPath(`/documents/${documentId}/versions`));
}

export async function getDocumentOcr(documentId: string): Promise<DocumentOcrResult> {
  return request<DocumentOcrResult>(apiPath(`/documents/${documentId}/ocr`));
}

export async function retryDocumentOcr(documentId: string): Promise<DocumentOcrResult> {
  return request<DocumentOcrResult>(apiPath(`/documents/${documentId}/ocr/retry`), {
    method: 'POST',
  });
}

export interface DocumentLlmSummary {
  document_id: string;
  summary: string;
  model: string;
  provider: string;
  prompt_hash: string;
  generated_at: string;
  pii_scrubbed: boolean;
}

export async function generateDocumentLlmSummary(documentId: string): Promise<DocumentLlmSummary> {
  return request<DocumentLlmSummary>(apiPath(`/documents/${documentId}/llm-summary`), {
    method: 'POST',
  });
}

export interface BatchLlmSummaryStatus {
  enabled: boolean;
  ready: boolean;
  blockers: string[];
  last_completed_at: string | null;
}

export interface BatchDocumentSummaryRun {
  id: string;
  organization_id: string;
  trigger_source: string;
  status: string;
  document_ids: string[];
  documents_queued: number;
  documents_succeeded: number;
  documents_failed: number;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface BatchDocumentSummaryEnqueueResponse {
  run: BatchDocumentSummaryRun;
  job_id: string;
}

export function getBatchLlmSummaryStatus() {
  return request<BatchLlmSummaryStatus>(apiPath('/documents/batch-llm-summaries/status'));
}

export function listBatchDocumentSummaryRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<{
    items: BatchDocumentSummaryRun[];
    total: number;
    page: number;
    page_size: number;
  }>(`${apiPath('/documents/batch-llm-summaries/runs')}?${params.toString()}`);
}

export function enqueueBatchDocumentSummaryRun(documentIds: string[] = []) {
  return request<BatchDocumentSummaryEnqueueResponse>(
    apiPath('/documents/batch-llm-summaries/run'),
    {
      method: 'POST',
      body: JSON.stringify({ document_ids: documentIds }),
    },
  );
}

export async function getDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
  return request<DocumentMetadata>(apiPath(`/documents/${documentId}/metadata`));
}

export async function getDocumentParsedCreditReport(
  documentId: string,
): Promise<DocumentParsedCreditReport> {
  return request<DocumentParsedCreditReport>(
    apiPath(`/documents/${documentId}/parsed-credit-report`),
  );
}

export interface DocumentCreditReportReparse {
  document_id: string;
  job_id: string;
  job_type: string;
  queued: boolean;
}

export async function reparseDocumentCreditReport(
  documentId: string,
): Promise<DocumentCreditReportReparse> {
  return request<DocumentCreditReportReparse>(
    apiPath(`/documents/${documentId}/parsed-credit-report/reparse`),
    { method: 'POST' },
  );
}

export async function compareDocumentParsedCreditReport(
  documentId: string,
): Promise<DocumentParsedCreditReportComparison> {
  return request<DocumentParsedCreditReportComparison>(
    apiPath(`/documents/${documentId}/parsed-credit-report/comparison`),
  );
}

export async function getDocumentMetro2Findings(
  documentId: string,
): Promise<DocumentMetro2Findings> {
  return request<DocumentMetro2Findings>(
    apiPath(`/documents/${documentId}/parsed-credit-report/metro2-findings`),
  );
}

export async function getDocumentFcraFindings(documentId: string): Promise<DocumentFcraFindings> {
  return request<DocumentFcraFindings>(
    apiPath(`/documents/${documentId}/parsed-credit-report/fcra-findings`),
  );
}

export async function getDocumentIdentityTheftFindings(
  documentId: string,
): Promise<DocumentIdentityTheftFindings> {
  return request<DocumentIdentityTheftFindings>(
    apiPath(`/documents/${documentId}/parsed-credit-report/identity-theft-findings`),
  );
}

export async function getDocumentParsedCreditReportAccountCandidates(
  documentId: string,
): Promise<DocumentParsedCreditReportAccountCandidates> {
  return request<DocumentParsedCreditReportAccountCandidates>(
    apiPath(`/documents/${documentId}/parsed-credit-report/account-candidates`),
  );
}

export async function createDocumentParsedCreditReportReviewTask(
  documentId: string,
): Promise<Task> {
  return request<Task>(apiPath(`/documents/${documentId}/parsed-credit-report/review-task`), {
    method: 'POST',
  });
}

export async function importParsedCreditReportAccounts(
  documentId: string,
  body: ImportParsedReportAccountsRequest = {},
): Promise<ImportParsedReportAccountsResponse> {
  return request<ImportParsedReportAccountsResponse>(
    apiPath(`/documents/${documentId}/parsed-credit-report/import-accounts`),
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  );
}

export async function extractDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
  return request<DocumentMetadata>(apiPath(`/documents/${documentId}/metadata/extract`), {
    method: 'POST',
  });
}

export interface DocumentMetadataReextract {
  document_id: string;
  job_id: string;
  job_type: string;
  queued: boolean;
}

export async function reextractDocumentMetadata(
  documentId: string,
): Promise<DocumentMetadataReextract> {
  return request<DocumentMetadataReextract>(
    apiPath(`/documents/${documentId}/metadata/reextract`),
    {
      method: 'POST',
    },
  );
}

export async function getDocumentResolutions(documentId: string): Promise<DocumentResolutions> {
  return request<DocumentResolutions>(apiPath(`/documents/${documentId}/resolutions`));
}

export async function resolveDocumentEntities(documentId: string): Promise<DocumentResolutions> {
  return request<DocumentResolutions>(apiPath(`/documents/${documentId}/resolutions/resolve`), {
    method: 'POST',
  });
}

export async function confirmDocumentResolution(
  documentId: string,
  resolutionId: string,
  matchedEntityId?: string,
): Promise<DocumentResolutions> {
  return request<DocumentResolutions>(
    apiPath(`/documents/${documentId}/resolutions/${resolutionId}/confirm`),
    {
      method: 'POST',
      body: matchedEntityId ? { matched_entity_id: matchedEntityId } : {},
    },
  );
}

export async function rejectDocumentResolution(
  documentId: string,
  resolutionId: string,
  reason?: string,
): Promise<DocumentResolutions> {
  return request<DocumentResolutions>(
    apiPath(`/documents/${documentId}/resolutions/${resolutionId}/reject`),
    {
      method: 'POST',
      body: reason ? { reason } : {},
    },
  );
}
