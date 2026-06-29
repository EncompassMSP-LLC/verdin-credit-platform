import type {
  ClassificationMethod,
  ClassificationStatus,
  DocumentProcessingStatus,
  DocumentType,
  PaginatedResponse,
} from '@verdin/shared';

import { apiPath, getApiBaseUrl, request, uploadRequest } from './http';

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
  classification_method: ClassificationMethod | null;
  classified_at: string | null;
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
  document_type?: DocumentType;
  classification_status?: ClassificationStatus;
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

export interface DocumentClassificationResult {
  document_id: string;
  document_type: DocumentType | null;
  confidence_score: number | null;
  classification_method: ClassificationMethod | null;
  classified_at: string | null;
  classified_by_id: string | null;
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

export async function getClassification(documentId: string): Promise<DocumentClassificationResult> {
  return request<DocumentClassificationResult>(apiPath(`/documents/${documentId}/classification`));
}

export async function classifyDocument(documentId: string): Promise<DocumentClassificationResult> {
  return request<DocumentClassificationResult>(apiPath(`/documents/${documentId}/classification`), {
    method: 'POST',
  });
}

export async function reclassifyDocument(
  documentId: string,
): Promise<DocumentClassificationResult> {
  return request<DocumentClassificationResult>(
    apiPath(`/documents/${documentId}/classification/reclassify`),
    { method: 'POST' },
  );
}
