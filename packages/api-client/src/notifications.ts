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
