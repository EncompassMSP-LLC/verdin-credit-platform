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

export function getOperationsReporting() {
  return request<OperationsReportingResponse>(apiPath('/reporting/operations'));
}
