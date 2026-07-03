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
