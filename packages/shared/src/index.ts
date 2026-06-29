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

export type CaseStatus = 'open' | 'active' | 'on_hold' | 'resolved' | 'closed';

export type CaseStage =
  | 'intake'
  | 'review'
  | 'evidence_gathering'
  | 'dispute_preparation'
  | 'awaiting_response'
  | 'monitoring'
  | 'complete';

export type CasePriority = 'low' | 'medium' | 'high' | 'critical';

export const CASE_STATUSES: CaseStatus[] = ['open', 'active', 'on_hold', 'resolved', 'closed'];

export const CASE_STAGES: CaseStage[] = [
  'intake',
  'review',
  'evidence_gathering',
  'dispute_preparation',
  'awaiting_response',
  'monitoring',
  'complete',
];

export const CASE_PRIORITIES: CasePriority[] = ['low', 'medium', 'high', 'critical'];

export const CASE_STATUS_LABELS: Record<CaseStatus, string> = {
  open: 'Open',
  active: 'Active',
  on_hold: 'On Hold',
  resolved: 'Resolved',
  closed: 'Closed',
};

export const CASE_STAGE_LABELS: Record<CaseStage, string> = {
  intake: 'Intake',
  review: 'Review',
  evidence_gathering: 'Evidence Gathering',
  dispute_preparation: 'Dispute Preparation',
  awaiting_response: 'Awaiting Response',
  monitoring: 'Monitoring',
  complete: 'Complete',
};

export const CASE_PRIORITY_LABELS: Record<CasePriority, string> = {
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  critical: 'Critical',
};

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
