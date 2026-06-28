import type { CaseStatus, PaginatedResponse } from '@verdin/shared';

import { apiPath, notImplemented } from './http';

export interface Case {
  id: string;
  title: string;
  description: string | null;
  status: CaseStatus;
  case_number: string | null;
  organization_id: string;
  account_id: string | null;
  assigned_to_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ListCasesParams {
  page?: number;
  page_size?: number;
}

export async function listCases(_params: ListCasesParams = {}): Promise<PaginatedResponse<Case>> {
  notImplemented(`GET ${apiPath('/cases')}`);
}

export async function getCase(_caseId: string): Promise<Case> {
  notImplemented(`GET ${apiPath('/cases/:id')}`);
}
