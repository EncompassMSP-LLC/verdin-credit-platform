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
  remarks: string | null;
}

export interface DocumentParsedCreditReportAccountCandidates {
  document_id: string;
  bureau: string;
  candidates: ParsedReportAccountCandidate[];
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

export async function compareDocumentParsedCreditReport(
  documentId: string,
): Promise<DocumentParsedCreditReportComparison> {
  return request<DocumentParsedCreditReportComparison>(
    apiPath(`/documents/${documentId}/parsed-credit-report/comparison`),
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

export async function extractDocumentMetadata(documentId: string): Promise<DocumentMetadata> {
  return request<DocumentMetadata>(apiPath(`/documents/${documentId}/metadata/extract`), {
    method: 'POST',
  });
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
