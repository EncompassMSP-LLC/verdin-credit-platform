export const APP_NAME = 'Verdin Credit Platform';
export const APP_VERSION = '4.2.0';

export type UserRole = 'owner' | 'admin' | 'case_manager' | 'reviewer' | 'read_only';

export const USER_ROLES: UserRole[] = ['owner', 'admin', 'case_manager', 'reviewer', 'read_only'];

export const ROLE_LABELS: Record<UserRole, string> = {
  owner: 'Owner',
  admin: 'Admin',
  case_manager: 'Case Manager',
  reviewer: 'Reviewer',
  read_only: 'Read Only',
};

export type CaseStatus = 'open' | 'in_review' | 'closed' | 'archived';

export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
}
