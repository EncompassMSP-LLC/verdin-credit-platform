import { apiPath, request } from './http';

export interface DashboardOverview {
  open_cases: number;
  active_accounts: number;
  documents: number;
  tasks_due_today: number;
  overdue_tasks: number;
  alert_count: number;
}

export interface DashboardCases {
  open: number;
  high_priority: number;
  created_today: number;
  closed_today: number;
  average_resolution_time_hours: number | null;
}

export interface DashboardAccounts {
  active: number;
  total: number;
  per_case: number;
}

export interface DashboardDocuments {
  total: number;
  processing: number;
  classification_confidence: number | null;
  entity_resolution_confidence: number | null;
  ai_ready: number;
  unresolved: number;
}

export interface DashboardTasks {
  pending: number;
  due_today: number;
  overdue: number;
}

export interface DashboardProcessing {
  ocr_queue: number;
  ocr_failed: number;
  classification_pending: number;
  metadata_pending: number;
  entity_resolution_pending: number;
}

export interface DashboardPerformance {
  cases_created_today: number;
  cases_closed_today: number;
  average_resolution_time_hours: number | null;
  documents_per_case: number;
  accounts_per_case: number;
}

export interface DashboardTimelineItem {
  id: string;
  occurred_at: string;
  event_type: string;
  title: string;
  description: string | null;
  case_id: string | null;
  case_number: string | null;
  document_id: string | null;
  document_title: string | null;
  file_name: string | null;
  metadata: Record<string, unknown>;
}

export type DashboardAlertType =
  'ocr_failure' | 'unmatched_entity' | 'document_review' | 'overdue_task';

export type DashboardAlertSeverity = 'critical' | 'high' | 'medium';

export interface DashboardAlertItem {
  id: string;
  alert_type: DashboardAlertType;
  severity: DashboardAlertSeverity;
  title: string;
  message: string;
  entity_type: 'task' | 'case' | 'document';
  entity_id: string;
  case_id: string | null;
  case_number: string | null;
}

export interface DashboardAlerts {
  total: number;
  items: DashboardAlertItem[];
}

export interface DashboardResponse {
  generated_at: string;
  refresh_seconds: number;
  overview: DashboardOverview;
  cases: DashboardCases;
  accounts: DashboardAccounts;
  documents: DashboardDocuments;
  timeline: DashboardTimelineItem[];
  tasks: DashboardTasks;
  processing: DashboardProcessing;
  performance: DashboardPerformance;
  alerts: DashboardAlerts;
}

export async function getDashboard(): Promise<DashboardResponse> {
  return request<DashboardResponse>(apiPath('/dashboard'));
}
