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

export interface ReinvestigationOutcomeAnalytics {
  total_responses: number;
  counts: Record<string, number>;
  deletion_rate: number;
  verification_rate: number;
  correction_rate: number;
  favorable_rate: number;
  no_response_rate: number;
  avg_days_to_response: number | null;
  median_days_to_response: number | null;
  measured_response_count: number;
}

export interface ReinvestigationOutcomeFilters {
  start: string | null;
  end: string | null;
  bureau: string | null;
  group_by: string | null;
}

export interface ReinvestigationOutcomeBureauBreakdown {
  bureau: string;
  analytics: ReinvestigationOutcomeAnalytics;
}

export interface ReinvestigationOutcomeAnalyticsResponse {
  generated_at: string;
  filters: ReinvestigationOutcomeFilters;
  analytics: ReinvestigationOutcomeAnalytics;
  by_bureau: ReinvestigationOutcomeBureauBreakdown[];
}

export interface ReinvestigationOutcomeAnalyticsParams {
  start?: string;
  end?: string;
  bureau?: string;
  group_by?: 'bureau';
}

export function getReinvestigationOutcomeAnalytics(
  params: ReinvestigationOutcomeAnalyticsParams = {},
) {
  const search = new URLSearchParams();
  if (params.start) search.set('start', params.start);
  if (params.end) search.set('end', params.end);
  if (params.bureau) search.set('bureau', params.bureau);
  if (params.group_by) search.set('group_by', params.group_by);
  const query = search.toString();
  return request<ReinvestigationOutcomeAnalyticsResponse>(
    apiPath(`/reporting/reinvestigation-outcomes${query ? `?${query}` : ''}`),
  );
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

export interface CrossOrgBenchmarkAnalyticsStatus {
  enabled: boolean;
  ready: boolean;
  blockers: string[];
}

export interface CrossOrgBenchmarkAnalytics {
  organization_id: string;
  active_clients: number;
  open_cases: number;
  resolved_accounts: number;
  cohort_average_active_clients: number;
  cohort_average_open_cases: number;
  cohort_average_resolved_accounts: number;
  active_clients_percentile: number;
  open_cases_percentile: number;
  resolved_accounts_percentile: number;
  organizations_evaluated: number;
}

export interface CrossOrgBenchmarkAnalyticsResponse {
  generated_at: string;
  benchmarks: CrossOrgBenchmarkAnalytics;
}

export interface CrossOrgBenchmarkRun {
  id: string;
  requested_by_id: string;
  trigger_source: string;
  status: string;
  organizations_evaluated: number;
  generated_at: string;
  error_message: string | null;
}

export interface CrossOrgBenchmarkRefreshResponse {
  generated_at: string;
  run: CrossOrgBenchmarkRun;
}

export function getCrossOrgBenchmarkAnalyticsStatus() {
  return request<CrossOrgBenchmarkAnalyticsStatus>(
    apiPath('/reporting/cross-org-benchmarks/status'),
  );
}

export function getCrossOrgBenchmarkAnalytics() {
  return request<CrossOrgBenchmarkAnalyticsResponse>(apiPath('/reporting/cross-org-benchmarks'));
}

export function listCrossOrgBenchmarkRuns() {
  return request<CrossOrgBenchmarkRun[]>(apiPath('/reporting/cross-org-benchmarks/runs'));
}

export function refreshCrossOrgBenchmarks() {
  return request<CrossOrgBenchmarkRefreshResponse>(
    apiPath('/reporting/cross-org-benchmarks/refresh'),
    {
      method: 'POST',
    },
  );
}

export interface UnredactedCrossOrgBenchmarkExportStatus {
  enabled: boolean;
  ready: boolean;
  cross_org_benchmark_ready: boolean;
  blockers: string[];
}

export interface UnredactedCrossOrgBenchmarkExportRun {
  id: string;
  organization_id: string;
  cross_org_benchmark_run_id: string;
  status: string;
  export_summary: string;
  export_reference_id: string | null;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  error_message: string | null;
}

export interface UnredactedCrossOrgBenchmarkExportRunResult {
  completed_at: string;
  run: UnredactedCrossOrgBenchmarkExportRun;
}

export interface UnredactedCrossOrgBenchmarkExportSubmitRequest {
  export_summary: string;
  export_reference_id?: string | null;
}

export function getUnredactedCrossOrgBenchmarkExportStatus() {
  return request<UnredactedCrossOrgBenchmarkExportStatus>(
    apiPath('/reporting/unredacted-cross-org-benchmark-exports/status'),
  );
}

export function listUnredactedCrossOrgBenchmarkExportRuns(params?: {
  page?: number;
  page_size?: number;
}) {
  const search = new URLSearchParams();
  if (params?.page) search.set('page', String(params.page));
  if (params?.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<{
    items: UnredactedCrossOrgBenchmarkExportRun[];
    total: number;
    page: number;
    page_size: number;
  }>(apiPath(`/reporting/unredacted-cross-org-benchmark-exports/runs${query ? `?${query}` : ''}`));
}

export function submitUnredactedCrossOrgBenchmarkExport(
  crossOrgBenchmarkRunId: string,
  body: UnredactedCrossOrgBenchmarkExportSubmitRequest,
) {
  return request<UnredactedCrossOrgBenchmarkExportRunResult>(
    apiPath(
      `/reporting/unredacted-cross-org-benchmark-exports/benchmark-runs/${crossOrgBenchmarkRunId}/start`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  );
}

export function approveUnredactedCrossOrgBenchmarkExportRun(runId: string) {
  return request<UnredactedCrossOrgBenchmarkExportRunResult>(
    apiPath(`/reporting/unredacted-cross-org-benchmark-exports/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export interface LiveUnredactedBenchmarkBlobExportStatus {
  enabled: boolean;
  ready: boolean;
  unredacted_export_ready: boolean;
  blockers: string[];
}

export interface LiveUnredactedBenchmarkBlobExportRun {
  id: string;
  organization_id: string;
  unredacted_export_run_id: string;
  status: string;
  export_summary: string;
  storage_key: string | null;
  content_type: string | null;
  byte_size: number | null;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  exported_at: string | null;
  error_message: string | null;
}

export interface LiveUnredactedBenchmarkBlobExportRunResult {
  completed_at: string;
  run: LiveUnredactedBenchmarkBlobExportRun;
}

export interface LiveUnredactedBenchmarkBlobExportSubmitRequest {
  export_summary: string;
}

export function getLiveUnredactedBenchmarkBlobExportStatus() {
  return request<LiveUnredactedBenchmarkBlobExportStatus>(
    apiPath('/reporting/live-unredacted-benchmark-blob-exports/status'),
  );
}

export function listLiveUnredactedBenchmarkBlobExportRuns(params?: {
  page?: number;
  page_size?: number;
}) {
  const search = new URLSearchParams();
  if (params?.page) search.set('page', String(params.page));
  if (params?.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<{
    items: LiveUnredactedBenchmarkBlobExportRun[];
    total: number;
    page: number;
    page_size: number;
  }>(apiPath(`/reporting/live-unredacted-benchmark-blob-exports/runs${query ? `?${query}` : ''}`));
}

export function submitLiveUnredactedBenchmarkBlobExport(
  unredactedExportRunId: string,
  body: LiveUnredactedBenchmarkBlobExportSubmitRequest,
) {
  return request<LiveUnredactedBenchmarkBlobExportRunResult>(
    apiPath(
      `/reporting/live-unredacted-benchmark-blob-exports/unredacted-export-runs/${unredactedExportRunId}/start`,
    ),
    {
      method: 'POST',
      body: JSON.stringify(body),
    },
  );
}

export function approveLiveUnredactedBenchmarkBlobExportRun(runId: string) {
  return request<LiveUnredactedBenchmarkBlobExportRunResult>(
    apiPath(`/reporting/live-unredacted-benchmark-blob-exports/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
