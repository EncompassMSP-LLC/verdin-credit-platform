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

export interface RevenueAnalytics {
  billing_enabled: boolean;
  billing_ready: boolean;
  stripe_customer_configured: boolean;
  stripe_subscription_configured: boolean;
  subscription_active: boolean;
  subscription_status: string;
  price_id: string | null;
  current_period_end: string | null;
  renewal_within_30_days: boolean | null;
  active_clients: number;
  portal_enabled_clients: number;
  portal_users: number;
  readiness_score: number;
}

export interface RevenueAnalyticsReportingResponse {
  generated_at: string;
  revenue_analytics: RevenueAnalytics;
}

export function getRevenueAnalyticsReporting() {
  return request<RevenueAnalyticsReportingResponse>(apiPath('/reporting/revenue'));
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

export interface PredictiveAnalyticsStatus {
  enabled: boolean;
  ready: boolean;
  blockers: string[];
}

export interface PredictiveOutcomes {
  cases_by_status: Record<string, number>;
  accounts_by_dispute_status: Record<string, number>;
  dispute_letters_by_status: Record<string, number>;
  total_cases: number;
  disputed_accounts: number;
  cases_closed_30d: number;
  cases_closed_90d: number;
  accounts_dispute_resolved: number;
  dispute_letters_sent: number;
  case_closure_rate_90d: number | null;
  dispute_resolution_rate: number | null;
  outcome_score: number;
  last_refreshed_at: string | null;
}

export interface PredictiveOutcomesReportingResponse {
  generated_at: string;
  predictive_outcomes: PredictiveOutcomes;
}

export interface PredictiveOutcomeRefreshRun {
  id: string;
  organization_id: string;
  trigger_source: string;
  status: string;
  started_at: string;
  completed_at: string;
  error_message: string | null;
}

export interface PredictiveOutcomeRefreshResult {
  refreshed_at: string;
  run: PredictiveOutcomeRefreshRun;
}

export function getPredictiveAnalyticsStatus() {
  return request<PredictiveAnalyticsStatus>(apiPath('/reporting/predictive/status'));
}

export function getPredictiveOutcomesReporting() {
  return request<PredictiveOutcomesReportingResponse>(apiPath('/reporting/predictive/outcomes'));
}

export function refreshPredictiveOutcomesReporting() {
  return request<PredictiveOutcomeRefreshResult>(apiPath('/reporting/predictive/refresh'), {
    method: 'POST',
  });
}
