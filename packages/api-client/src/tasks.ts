import type { PaginatedResponse, TaskPriority, TaskStatus } from '@verdin/shared';

import { apiPath, request } from './http';

export interface Task {
  id: string;
  organization_id: string;
  case_id: string | null;
  account_id: string | null;
  document_id: string | null;
  assigned_user_id: string | null;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  completed_at: string | null;
  completed_by_id: string | null;
  source_module: string | null;
  source_event_id: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  created_by_id: string | null;
  updated_by_id: string | null;
}

export interface CreateTaskInput {
  title: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string | null;
  case_id?: string | null;
  account_id?: string | null;
  document_id?: string | null;
  assigned_user_id?: string | null;
  source_module?: string | null;
  source_event_id?: string | null;
}

export interface UpdateTaskInput {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string | null;
  case_id?: string | null;
  account_id?: string | null;
  document_id?: string | null;
  assigned_user_id?: string | null;
  source_module?: string | null;
  source_event_id?: string | null;
}

export interface ListTasksParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  case_id?: string;
  account_id?: string;
  document_id?: string;
  assigned_user_id?: string;
  due_before?: string;
  due_after?: string;
  overdue?: boolean;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

function buildQuery(params: ListTasksParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function createTask(input: CreateTaskInput): Promise<Task> {
  return request<Task>(apiPath('/tasks'), { method: 'POST', body: input });
}

export async function listTasks(params: ListTasksParams = {}): Promise<PaginatedResponse<Task>> {
  return request<PaginatedResponse<Task>>(`${apiPath('/tasks')}${buildQuery(params)}`);
}

export async function getTask(taskId: string): Promise<Task> {
  return request<Task>(apiPath(`/tasks/${taskId}`));
}

export async function updateTask(taskId: string, input: UpdateTaskInput): Promise<Task> {
  return request<Task>(apiPath(`/tasks/${taskId}`), { method: 'PATCH', body: input });
}

export async function completeTask(taskId: string): Promise<Task> {
  return request<Task>(apiPath(`/tasks/${taskId}/complete`), { method: 'POST' });
}

export async function reopenTask(taskId: string): Promise<Task> {
  return request<Task>(apiPath(`/tasks/${taskId}/reopen`), { method: 'POST' });
}

export async function deleteTask(taskId: string): Promise<void> {
  await request<void>(apiPath(`/tasks/${taskId}`), { method: 'DELETE' });
}
