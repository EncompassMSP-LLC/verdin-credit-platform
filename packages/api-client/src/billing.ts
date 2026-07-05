import { apiPath, request } from './http';

export type SubscriptionStatus =
  'none' | 'active' | 'trialing' | 'past_due' | 'canceled' | 'incomplete' | 'unpaid';

export interface BillingStatus {
  enabled: boolean;
  ready: boolean;
  provider: string;
  default_price_id: string | null;
  blockers: string[];
}

export interface OrganizationBillingSummary {
  enabled: boolean;
  ready: boolean;
  stripe_customer_id?: string | null;
  stripe_subscription_id?: string | null;
  subscription_status?: SubscriptionStatus;
  price_id?: string | null;
  current_period_end?: string | null;
}

export interface BillingSetupResponse {
  organization_id: string;
  stripe_customer_id: string;
  created: boolean;
}

export interface BillingSubscribeInput {
  price_id?: string | null;
}

export interface BillingSubscribeResponse {
  organization_id: string;
  stripe_customer_id: string;
  stripe_subscription_id: string;
  subscription_status: SubscriptionStatus;
  price_id: string | null;
  current_period_end: string | null;
}

export function getBillingStatus() {
  return request<BillingStatus>(apiPath('/billing/status'));
}

export function setupOrganizationBilling() {
  return request<BillingSetupResponse>(apiPath('/billing/setup'), {
    method: 'POST',
  });
}

export function subscribeOrganizationBilling(input: BillingSubscribeInput = {}) {
  return request<BillingSubscribeResponse>(apiPath('/billing/subscribe'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export interface BillingUsageMetricTotal {
  metric_name: string;
  total_quantity: number;
}

export interface BillingUsageSummary {
  organization_id: string;
  metering_enabled: boolean;
  stripe_customer_configured: boolean;
  total_events: number;
  metrics: BillingUsageMetricTotal[];
  first_recorded_at: string | null;
  last_recorded_at: string | null;
}

export interface BillingUsageRecordInput {
  metric_name: string;
  quantity?: number;
  source?: string;
}

export interface BillingUsageRecordResponse {
  id: string;
  organization_id: string;
  metric_name: string;
  quantity: number;
  source: string;
  recorded_at: string;
}

export function getBillingUsageSummary() {
  return request<BillingUsageSummary>(apiPath('/billing/usage/summary'));
}

export function recordBillingUsageEvent(input: BillingUsageRecordInput) {
  return request<BillingUsageRecordResponse>(apiPath('/billing/usage/events'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export interface BillingInvoicingStatus {
  enabled: boolean;
  ready: boolean;
  billing_ready: boolean;
  blockers: string[];
}

export type BillingInvoicingRunKind = 'invoice_cycle' | 'dunning_reminder';

export interface BillingInvoicingRun {
  id: string;
  organization_id: string;
  run_kind: BillingInvoicingRunKind;
  trigger_source: 'manual' | 'scheduled';
  status: 'pending' | 'running' | 'completed' | 'failed';
  invoices_prepared: number;
  dunning_reminders_queued: number;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface BillingInvoicingRunInput {
  run_kind?: BillingInvoicingRunKind;
}

export interface BillingInvoicingRunResult {
  completed_at: string;
  run: BillingInvoicingRun;
}

export function getBillingInvoicingStatus() {
  return request<BillingInvoicingStatus>(apiPath('/billing/invoicing/status'));
}

export function listBillingInvoicingRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<{ items: BillingInvoicingRun[]; total: number; page: number; page_size: number }>(
    apiPath(`/billing/invoicing/runs?${params.toString()}`),
  );
}

export function runBillingInvoicingCycle(input: BillingInvoicingRunInput = {}) {
  return request<BillingInvoicingRunResult>(apiPath('/billing/invoicing/run'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export interface BillingInvoiceCollectionStatus {
  enabled: boolean;
  ready: boolean;
  invoicing_ready: boolean;
  blockers: string[];
}

export type BillingInvoiceCollectionRunKind = 'invoice_pdf' | 'payment_reminder';

export interface BillingInvoiceCollectionRun {
  id: string;
  organization_id: string;
  run_kind: BillingInvoiceCollectionRunKind;
  trigger_source: 'manual' | 'scheduled';
  status: 'pending' | 'running' | 'completed' | 'failed';
  invoices_pdf_generated: number;
  payment_reminders_queued: number;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface BillingInvoiceCollectionRunInput {
  run_kind?: BillingInvoiceCollectionRunKind;
}

export interface BillingInvoiceCollectionRunResult {
  completed_at: string;
  run: BillingInvoiceCollectionRun;
}

export function getBillingInvoiceCollectionStatus() {
  return request<BillingInvoiceCollectionStatus>(apiPath('/billing/collection/status'));
}

export function listBillingInvoiceCollectionRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<{
    items: BillingInvoiceCollectionRun[];
    total: number;
    page: number;
    page_size: number;
  }>(apiPath(`/billing/collection/runs?${params.toString()}`));
}

export function runBillingInvoiceCollection(input: BillingInvoiceCollectionRunInput = {}) {
  return request<BillingInvoiceCollectionRunResult>(apiPath('/billing/collection/run'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export type StripeInvoicePdfRunStatus = 'pending_approval' | 'generated' | 'rejected' | 'failed';

export interface StripeInvoicePdfGateStatus {
  enabled: boolean;
  ready: boolean;
  collection_ready: boolean;
  blockers: string[];
}

export interface StripeInvoicePdfRun {
  id: string;
  organization_id: string;
  collection_run_id: string;
  status: StripeInvoicePdfRunStatus;
  generation_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  generated_at: string | null;
  error_message: string | null;
}

export interface StripeInvoicePdfRunList {
  total: number;
  page: number;
  page_size: number;
  items: StripeInvoicePdfRun[];
}

export interface StripeInvoicePdfInput {
  generation_summary: string;
}

export interface StripeInvoicePdfRunResult {
  completed_at: string;
  run: StripeInvoicePdfRun;
}

export function getStripeInvoicePdfStatus() {
  return request<StripeInvoicePdfGateStatus>(apiPath('/billing/invoice-pdf/status'));
}

export function listStripeInvoicePdfRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<StripeInvoicePdfRunList>(
    apiPath(`/billing/invoice-pdf/runs?${params.toString()}`),
  );
}

export function submitStripeInvoicePdfRun(collectionRunId: string, input: StripeInvoicePdfInput) {
  return request<StripeInvoicePdfRunResult>(
    apiPath(`/billing/invoice-pdf/collection-runs/${collectionRunId}/generate`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveStripeInvoicePdfRun(runId: string) {
  return request<StripeInvoicePdfRunResult>(apiPath(`/billing/invoice-pdf/runs/${runId}/approve`), {
    method: 'POST',
  });
}

export type StripeTaxCalculationRunStatus =
  'pending_approval' | 'calculated' | 'rejected' | 'failed';

export interface StripeTaxCalculationGateStatus {
  enabled: boolean;
  ready: boolean;
  invoice_pdf_ready: boolean;
  blockers: string[];
}

export interface StripeTaxCalculationRun {
  id: string;
  organization_id: string;
  invoice_pdf_run_id: string;
  status: StripeTaxCalculationRunStatus;
  calculation_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  calculated_at: string | null;
  error_message: string | null;
}

export interface StripeTaxCalculationInput {
  calculation_summary: string;
}

export interface StripeTaxCalculationRunResult {
  completed_at: string;
  run: StripeTaxCalculationRun;
}

export interface StripeTaxCalculationRunList {
  items: StripeTaxCalculationRun[];
  total: number;
  page: number;
  page_size: number;
}

export function getStripeTaxCalculationStatus() {
  return request<StripeTaxCalculationGateStatus>(apiPath('/billing/tax-calculation/status'));
}

export function listStripeTaxCalculationRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<StripeTaxCalculationRunList>(
    apiPath(`/billing/tax-calculation/runs?${params.toString()}`),
  );
}

export function submitStripeTaxCalculationRun(
  invoicePdfRunId: string,
  input: StripeTaxCalculationInput,
) {
  return request<StripeTaxCalculationRunResult>(
    apiPath(`/billing/tax-calculation/pdf-runs/${invoicePdfRunId}/calculate`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveStripeTaxCalculationRun(runId: string) {
  return request<StripeTaxCalculationRunResult>(
    apiPath(`/billing/tax-calculation/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}

export type StripeLiveTaxApiRunStatus = 'pending_approval' | 'invoked' | 'rejected' | 'failed';

export interface StripeLiveTaxApiGateStatus {
  enabled: boolean;
  ready: boolean;
  tax_calculation_ready: boolean;
  blockers: string[];
}

export interface StripeLiveTaxApiRun {
  id: string;
  organization_id: string;
  stripe_tax_calculation_run_id: string;
  status: StripeLiveTaxApiRunStatus;
  invocation_summary: string;
  requested_by_user_id: string | null;
  approved_by_user_id: string | null;
  requested_at: string | null;
  approved_at: string | null;
  invoked_at: string | null;
  error_message: string | null;
}

export interface StripeLiveTaxApiInvokeInput {
  invocation_summary: string;
}

export interface StripeLiveTaxApiRunResult {
  completed_at: string;
  run: StripeLiveTaxApiRun;
}

export interface StripeLiveTaxApiRunList {
  items: StripeLiveTaxApiRun[];
  total: number;
  page: number;
  page_size: number;
}

export function getStripeLiveTaxApiStatus() {
  return request<StripeLiveTaxApiGateStatus>(apiPath('/billing/live-tax-api/status'));
}

export function listStripeLiveTaxApiRuns(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return request<StripeLiveTaxApiRunList>(
    apiPath(`/billing/live-tax-api/runs?${params.toString()}`),
  );
}

export function invokeStripeLiveTaxApiFromTaxCalculationRun(
  stripeTaxCalculationRunId: string,
  input: StripeLiveTaxApiInvokeInput,
) {
  return request<StripeLiveTaxApiRunResult>(
    apiPath(`/billing/live-tax-api/tax-calculation-runs/${stripeTaxCalculationRunId}/invoke`),
    {
      method: 'POST',
      body: JSON.stringify(input),
    },
  );
}

export function approveStripeLiveTaxApiRun(runId: string) {
  return request<StripeLiveTaxApiRunResult>(
    apiPath(`/billing/live-tax-api/runs/${runId}/approve`),
    {
      method: 'POST',
    },
  );
}
