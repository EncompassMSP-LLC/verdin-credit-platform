'use client';

import {
  getUnreadNotificationCount,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  type Notification,
  type NotificationCategory,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useLenderAuth } from '@/lib/lender/auth';
import type { LenderNotification } from '@/lib/lender/types';

function categorySeverity(category: NotificationCategory): LenderNotification['severity'] {
  if (category === 'dispute') return 'warn';
  if (category === 'workflow' || category === 'task') return 'info';
  if (category === 'document') return 'success';
  return 'info';
}

function actionHref(actionUrl: string | null): string {
  if (!actionUrl) return '/lender/dashboard';
  if (actionUrl.startsWith('/lender')) return actionUrl;
  const lower = actionUrl.toLowerCase();
  if (lower.includes('referral')) return '/lender/referrals';
  if (lower.includes('readiness')) return '/lender/readiness';
  if (lower.includes('pipeline')) return '/lender/pipeline';
  if (lower.includes('message')) return '/lender/messages';
  if (lower.includes('document')) return '/lender/documents';
  return '/lender/dashboard';
}

export function mapPlatformNotification(n: Notification): LenderNotification {
  return {
    id: n.id,
    title: n.title,
    body: n.body ?? '',
    at: n.created_at,
    read: Boolean(n.read_at),
    href: actionHref(n.action_url),
    severity: categorySeverity(n.category),
  };
}

export function useLenderNotifications(options?: { unreadOnly?: boolean }) {
  const { isAuthenticated, authMode } = useLenderAuth();
  const unreadOnly = options?.unreadOnly === true;
  return useQuery({
    queryKey: ['lender', 'notifications', { unreadOnly }],
    enabled: isAuthenticated && authMode === 'platform',
    queryFn: async () => {
      const response = await listNotifications({
        page: 1,
        page_size: 50,
        unread_only: unreadOnly || undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      });
      return response.items.map(mapPlatformNotification);
    },
  });
}

export function useLenderUnreadNotificationCount() {
  const { isAuthenticated, authMode } = useLenderAuth();
  return useQuery({
    queryKey: ['lender', 'notifications', 'unread-count'],
    enabled: isAuthenticated && authMode === 'platform',
    queryFn: async () => {
      const response = await getUnreadNotificationCount();
      return response.unread_count;
    },
    refetchInterval: 60_000,
  });
}

export function useMarkLenderNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notificationId: string) => markNotificationRead(notificationId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['lender', 'notifications'] });
    },
  });
}

export function useMarkAllLenderNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => markAllNotificationsRead(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['lender', 'notifications'] });
    },
  });
}
