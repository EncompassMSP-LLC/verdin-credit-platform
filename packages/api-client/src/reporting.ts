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
