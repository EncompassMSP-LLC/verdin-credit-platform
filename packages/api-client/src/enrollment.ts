import { apiPath, request } from './http';
import type { PortalTokenResponse } from './portal';

export interface ClientEnrollmentStatus {
  enabled: boolean;
  ready: boolean;
  payment_required: boolean;
  checkout_available: boolean;
  organization_slug: string;
  price_id: string | null;
  annual_credit_report_url: string;
  blockers: string[];
}

export interface ClientEnrollmentIntakeInput {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string | null;
  mailing_address_line1: string;
  mailing_address_line2?: string | null;
  mailing_city: string;
  mailing_state: string;
  mailing_postal_code: string;
}

export interface ClientEnrollmentCheckoutResult {
  enrollment_id: string;
  checkout_session_id: string;
  checkout_url: string;
}

export interface ClientEnrollmentSession {
  enrollment_id: string;
  status: string;
  payment_status: string | null;
  case_id: string | null;
  client_id: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface ClientEnrollmentCompleteResult {
  enrollment: ClientEnrollmentSession;
  portal: PortalTokenResponse;
}

export function getClientEnrollmentStatus() {
  return request<ClientEnrollmentStatus>(apiPath('/enrollment/status'));
}

export function startClientEnrollmentCheckout(input: ClientEnrollmentIntakeInput) {
  return request<ClientEnrollmentCheckoutResult>(apiPath('/enrollment/checkout'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function registerClientEnrollment(input: ClientEnrollmentIntakeInput) {
  return request<ClientEnrollmentCompleteResult>(apiPath('/enrollment/register'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function getClientEnrollmentCheckoutSession(sessionId: string) {
  return request<ClientEnrollmentSession>(apiPath(`/enrollment/checkout/${sessionId}`));
}

export function completeClientEnrollment(sessionId: string) {
  return request<ClientEnrollmentCompleteResult>(apiPath('/enrollment/complete'), {
    method: 'POST',
    body: JSON.stringify({ session_id: sessionId }),
  });
}
