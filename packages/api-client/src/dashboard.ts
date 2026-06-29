import { apiPath, request } from './http';

export interface DashboardKpis {
  open_cases: number;
  active_accounts: number;
  pending_tasks: number;
  documents_processing: number;
  ocr_queue: number;
  average_resolution_time_hours: number | null;
}

export interface DashboardProcessing {
  uploads_today: number;
  ocr_running: number;
  ocr_failed: number;
  classification_pending: number;
  metadata_pending: number;
  entity_resolution_pending: number;
}

export type DashboardQueueEntityType = 'task' | 'case' | 'document';

export interface DashboardQueueItem {
  id: string;
  title: string;
  subtitle: string | null;
  entity_type: DashboardQueueEntityType;
  priority: string | null;
  due_date: string | null;
  case_id: string | null;
  case_number: string | null;
}

export interface DashboardWorkQueue {
  overdue_tasks: DashboardQueueItem[];
  high_priority_cases: DashboardQueueItem[];
  documents_requiring_review: DashboardQueueItem[];
  ocr_failures: DashboardQueueItem[];
  unresolved_entity_matches: DashboardQueueItem[];
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
  metadata: Record<string, unknown>;
}

export interface DashboardAi {
  documents_classified: number;
  metadata_extracted: number;
  entity_resolution_rate: number;
  average_confidence: number | null;
  ai_ready_documents: number;
}

export interface DashboardPerformance {
  average_accounts_per_case: number;
  average_documents_per_case: number;
  cases_opened_this_week: number;
  cases_completed_this_month: number;
  resolution_rate: number;
  processing_throughput: number;
}

export interface DashboardResponse {
  generated_at: string;
  refresh_seconds: number;
  kpis: DashboardKpis;
  processing: DashboardProcessing;
  tasks: DashboardWorkQueue;
  timeline: DashboardTimelineItem[];
  ai: DashboardAi;
  performance: DashboardPerformance;
}

export async function getDashboard(): Promise<DashboardResponse> {
  return request<DashboardResponse>(apiPath('/dashboard'));
}
