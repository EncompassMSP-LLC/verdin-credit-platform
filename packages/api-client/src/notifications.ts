import type { PaginatedResponse } from '@verdin/shared';

import { apiPath, request } from './http';

export type NotificationCategory = 'system' | 'task' | 'dispute' | 'document' | 'workflow';

export interface Notification {
  id: string;
  organization_id: string;
  recipient_user_id: string;
  title: string;
  body: string | null;
  category: NotificationCategory;
  read_at: string | null;
  entity_type: string | null;
  entity_id: string | null;
  source_module: string | null;
  action_url: string | null;
  created_at: string;
  updated_at: string;
  email_delivery?: EmailDeliveryAttempt | null;
  sms_delivery?: SmsDeliveryAttempt | null;
}

export interface CreateNotificationInput {
  recipient_user_id: string;
  title: string;
  body?: string | null;
  category?: NotificationCategory;
  entity_type?: string | null;
  entity_id?: string | null;
  source_module?: string | null;
  action_url?: string | null;
  deliver_email?: boolean;
  deliver_sms?: boolean;
}

export interface EmailDeliveryAttempt {
  attempted: boolean;
  status?: string | null;
  delivery_log_id?: string | null;
  error?: string | null;
}

export interface EmailDeliveryLog {
  id: string;
  organization_id: string;
  notification_id: string | null;
  recipient_user_id: string | null;
  recipient_email: string;
  subject: string;
  provider: string;
  status: string;
  provider_message_id: string | null;
  error_message: string | null;
  sent_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface SendNotificationEmailInput {
  recipient_user_id: string;
  subject: string;
  body: string;
  notification_id?: string | null;
}

export interface ListNotificationsParams {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
  category?: NotificationCategory;
  sort_by?: 'created_at' | 'read_at';
  sort_order?: 'asc' | 'desc';
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface EmailDeliveryStatus {
  enabled: boolean;
  ready: boolean;
  provider: string;
  from_address: string | null;
  blockers: string[];
}

export interface SmsDeliveryAttempt {
  attempted: boolean;
  status?: string | null;
  delivery_log_id?: string | null;
  error?: string | null;
}

export interface SmsDeliveryLog {
  id: string;
  organization_id: string;
  notification_id: string | null;
  recipient_user_id: string | null;
  recipient_phone: string;
  body: string;
  provider: string;
  status: string;
  provider_message_id: string | null;
  error_message: string | null;
  sent_by_user_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface SendNotificationSmsInput {
  recipient_user_id: string;
  body: string;
  notification_id?: string | null;
}

export interface SmsDeliveryStatus {
  enabled: boolean;
  ready: boolean;
  provider: string;
  from_number: string | null;
  blockers: string[];
}

function buildQuery(params: ListNotificationsParams): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value));
    }
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export function listNotifications(params: ListNotificationsParams = {}) {
  return request<PaginatedResponse<Notification>>(apiPath(`/notifications${buildQuery(params)}`));
}

export function getUnreadNotificationCount() {
  return request<UnreadCountResponse>(apiPath('/notifications/unread-count'));
}

export function markNotificationRead(notificationId: string) {
  return request<Notification>(apiPath(`/notifications/${notificationId}/read`), {
    method: 'POST',
  });
}

export function markAllNotificationsRead() {
  return request<UnreadCountResponse>(apiPath('/notifications/mark-all-read'), {
    method: 'POST',
  });
}

export function createNotification(input: CreateNotificationInput) {
  return request<Notification>(apiPath('/notifications'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function getNotificationEmailDeliveryStatus() {
  return request<EmailDeliveryStatus>(apiPath('/notifications/email/status'));
}

export function sendNotificationEmail(input: SendNotificationEmailInput) {
  return request<EmailDeliveryLog>(apiPath('/notifications/email/send'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function listNotificationEmailDeliveries(
  params: { page?: number; page_size?: number } = {},
) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<EmailDeliveryLog>>(
    apiPath(`/notifications/email/deliveries${query ? `?${query}` : ''}`),
  );
}

export function getNotificationSmsDeliveryStatus() {
  return request<SmsDeliveryStatus>(apiPath('/notifications/sms/status'));
}

export function sendNotificationSms(input: SendNotificationSmsInput) {
  return request<SmsDeliveryLog>(apiPath('/notifications/sms/send'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}

export function listNotificationSmsDeliveries(params: { page?: number; page_size?: number } = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<SmsDeliveryLog>>(
    apiPath(`/notifications/sms/deliveries${query ? `?${query}` : ''}`),
  );
}

export interface SmsMarketingCampaignStatus {
  enabled: boolean;
  ready: boolean;
  sms_delivery_ready: boolean;
  blockers: string[];
}

export type SmsMarketingCampaignRunStatus = 'pending' | 'running' | 'completed' | 'failed';
export type SmsMarketingTriggerSource = 'manual' | 'scheduled';

export interface SmsMarketingCampaignRun {
  id: string;
  organization_id: string;
  campaign_name: string;
  message_body: string;
  recipient_user_ids: string[];
  trigger_source: SmsMarketingTriggerSource;
  status: SmsMarketingCampaignRunStatus;
  recipients_queued: number;
  messages_sent: number;
  messages_failed: number;
  performed_by_user_id: string | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface SmsMarketingCampaignRunInput {
  campaign_name: string;
  message_body: string;
  recipient_user_ids: string[];
}

export interface SmsMarketingCampaignRunResult {
  completed_at: string;
  run: SmsMarketingCampaignRun;
}

export function getSmsMarketingCampaignStatus() {
  return request<SmsMarketingCampaignStatus>(apiPath('/notifications/sms-campaigns/status'));
}

export function listSmsMarketingCampaignRuns(params: { page?: number; page_size?: number } = {}) {
  const search = new URLSearchParams();
  if (params.page) search.set('page', String(params.page));
  if (params.page_size) search.set('page_size', String(params.page_size));
  const query = search.toString();
  return request<PaginatedResponse<SmsMarketingCampaignRun>>(
    apiPath(`/notifications/sms-campaigns/runs${query ? `?${query}` : ''}`),
  );
}

export function runSmsMarketingCampaign(input: SmsMarketingCampaignRunInput) {
  return request<SmsMarketingCampaignRunResult>(apiPath('/notifications/sms-campaigns/run'), {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
