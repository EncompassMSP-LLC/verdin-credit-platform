import { apiPath, request } from './http';

export interface ClientReportingMetrics {
  total: number;
  active: number;
  portal_enabled: number;
}

export interface NotificationReportingMetrics {
  unread_total: number;
  created_today: number;
}

export interface OperationsReporting {
  clients: ClientReportingMetrics;
  dispute_accounts: Record<string, number>;
  dispute_letters: Record<string, number>;
  notifications: NotificationReportingMetrics;
  portal_users: number;
}

export interface OperationsReportingResponse {
  generated_at: string;
  operations: OperationsReporting;
}

export interface BureauPerformanceItem {
  bureau: string;
  total_accounts: number;
  dispute_status: Record<string, number>;
  sent_letters: number;
  resolved_accounts: number;
}

export interface BureauPerformanceReporting {
  bureaus: BureauPerformanceItem[];
  total_accounts: number;
}

export interface BureauPerformanceReportingResponse {
  generated_at: string;
  bureau_performance: BureauPerformanceReporting;
}

export interface TeamMemberProductivity {
  user_id: string;
  email: string;
  full_name: string;
  open_tasks: number;
  completed_tasks_30d: number;
  assigned_open_cases: number;
  closed_cases_30d: number;
}

export interface TeamProductivityReporting {
  members: TeamMemberProductivity[];
  open_tasks_total: number;
  completed_tasks_30d_total: number;
  assigned_open_cases_total: number;
  closed_cases_30d_total: number;
}

export interface TeamProductivityReportingResponse {
  generated_at: string;
  team_productivity: TeamProductivityReporting;
}

export interface EnterpriseReportingStatus {
  enterprise_reporting_enabled: boolean;
  capabilities: string[];
  deferred_capabilities: string[];
}

export interface MaterializedReportingStatus {
  enabled: boolean;
  views: string[];
  last_refreshed_at: string | null;
}

export interface ReportingMvRefreshRun {
  id: string;
  organization_id: string | null;
  trigger_source: string;
  status: string;
  views_refreshed: number;
  started_at: string;
  completed_at: string;
  error_message: string | null;
}

export interface ReportingMvRefreshResult {
  views_refreshed: number;
  run: ReportingMvRefreshRun;
}

export function getOperationsReporting() {
  return request<OperationsReportingResponse>(apiPath('/reporting/operations'));
}

export function getEnterpriseReportingStatus() {
  return request<EnterpriseReportingStatus>(apiPath('/reporting/status'));
}

export function getBureauPerformanceReporting() {
  return request<BureauPerformanceReportingResponse>(apiPath('/reporting/bureau-performance'));
}

export function getTeamProductivityReporting() {
  return request<TeamProductivityReportingResponse>(apiPath('/reporting/team-productivity'));
}

export function getMaterializedReportingStatus() {
  return request<MaterializedReportingStatus>(apiPath('/reporting/materialized-views/status'));
}

export function listMaterializedReportingRefreshRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<{
    items: ReportingMvRefreshRun[];
    total: number;
    page: number;
    page_size: number;
  }>(`${apiPath('/reporting/materialized-views/runs')}?${params.toString()}`);
}

export function refreshMaterializedReportingViews() {
  return request<ReportingMvRefreshResult>(apiPath('/reporting/materialized-views/refresh'), {
    method: 'POST',
  });
}
