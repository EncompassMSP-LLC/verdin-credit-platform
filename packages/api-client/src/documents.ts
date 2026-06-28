import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, notImplemented } from './http';

export interface Document {
  id: string;
  title: string;
  file_name: string;
  mime_type: string | null;
  file_size: number | null;
  case_id: string;
  created_at: string;
}

export interface ListDocumentsParams {
  case_id?: string;
  page?: number;
  page_size?: number;
}

export async function listDocuments(
  _params: ListDocumentsParams = {},
): Promise<PaginatedResponse<Document>> {
  notImplemented(`GET ${apiPath('/documents')}`);
}

export async function getDocument(_documentId: string): Promise<Document> {
  notImplemented(`GET ${apiPath('/documents/:id')}`);
}
