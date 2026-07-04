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
