import type { PaginatedResponse, TaskPriority, TaskStatus } from '@verdin/shared';

import { apiPath, notImplemented } from './http';

export interface Task {
  id: string;
  title: string;
  description: string | null;
  status: TaskStatus;
  priority: TaskPriority;
  due_date: string | null;
  case_id: string;
  assigned_to_id: string | null;
  created_at: string;
}

export interface ListTasksParams {
  case_id?: string;
  page?: number;
  page_size?: number;
}

export async function listTasks(_params: ListTasksParams = {}): Promise<PaginatedResponse<Task>> {
  notImplemented(`GET ${apiPath('/tasks')}`);
}

export async function getTask(_taskId: string): Promise<Task> {
  notImplemented(`GET ${apiPath('/tasks/:id')}`);
}
