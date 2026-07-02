import type { CasePriority, CaseStage, CaseStatus, PaginatedResponse } from '@verdin/shared';

import { apiPath, request } from './http';

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
