'use client';

import {
  getPortalUnreadNotificationCount,
  listPortalNotifications,
  markAllPortalNotificationsRead,
  markPortalNotificationRead,
  type PortalNotification,
  type PortalNotificationCategory,
} from '@verdin/api-client';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { usePlatformAuth } from '@/lib/platform/auth';

export function safePortalHref(actionUrl: string | null | undefined): string {
  if (!actionUrl) return '/portal/dashboard';
  if (!actionUrl.startsWith('/portal')) return '/portal/dashboard';
  if (actionUrl.includes('..') || actionUrl.includes('\\')) return '/portal/dashboard';
  return actionUrl;
}

export function categoryLabel(category: PortalNotificationCategory): string {
  switch (category) {
    case 'document':
      return 'Document';
    case 'task':
      return 'Task';
    case 'dispute':
      return 'Dispute';
    case 'workflow':
      return 'Workflow';
    default:
      return 'System';
  }
}

export function usePortalNotifications(options?: { unreadOnly?: boolean; page?: number }) {
  const { isAuthenticated } = usePlatformAuth();
  const unreadOnly = options?.unreadOnly === true;
  const page = options?.page ?? 1;
  return useQuery({
    queryKey: ['portal', 'notifications', { unreadOnly, page }],
    enabled: isAuthenticated,
    queryFn: async () => {
      const response = await listPortalNotifications({
        page,
        page_size: 20,
        unread_only: unreadOnly || undefined,
        sort_by: 'created_at',
        sort_order: 'desc',
      });
      return response;
    },
  });
}

export function usePortalUnreadNotificationCount() {
  const { isAuthenticated } = usePlatformAuth();
  return useQuery({
    queryKey: ['portal', 'notifications', 'unread-count'],
    enabled: isAuthenticated,
    queryFn: async () => {
      const response = await getPortalUnreadNotificationCount();
      return response.unread_count;
    },
    refetchInterval: 60_000,
  });
}

export function useMarkPortalNotificationRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (notificationId: string) => markPortalNotificationRead(notificationId),
    onMutate: async (notificationId) => {
      await queryClient.cancelQueries({ queryKey: ['portal', 'notifications'] });
      const previousLists = queryClient.getQueriesData<{
        items: PortalNotification[];
        total: number;
      }>({ queryKey: ['portal', 'notifications'] });
      const previousUnread = queryClient.getQueryData<number>([
        'portal',
        'notifications',
        'unread-count',
      ]);

      queryClient.setQueriesData<{ items: PortalNotification[]; total: number }>(
        { queryKey: ['portal', 'notifications'] },
        (current) => {
          if (!current?.items) return current;
          return {
            ...current,
            items: current.items.map((item) =>
              item.id === notificationId && !item.read_at
                ? { ...item, read_at: new Date().toISOString() }
                : item,
            ),
          };
        },
      );
      if (typeof previousUnread === 'number' && previousUnread > 0) {
        queryClient.setQueryData(['portal', 'notifications', 'unread-count'], previousUnread - 1);
      }

      return { previousLists, previousUnread };
    },
    onError: (_error, _id, context) => {
      context?.previousLists?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data);
      });
      if (context?.previousUnread !== undefined) {
        queryClient.setQueryData(
          ['portal', 'notifications', 'unread-count'],
          context.previousUnread,
        );
      }
    },
    onSettled: async () => {
      await queryClient.invalidateQueries({ queryKey: ['portal', 'notifications'] });
    },
  });
}

export function useMarkAllPortalNotificationsRead() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => markAllPortalNotificationsRead(),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['portal', 'notifications'] });
      const previousLists = queryClient.getQueriesData<{
        items: PortalNotification[];
        total: number;
      }>({ queryKey: ['portal', 'notifications'] });
      const previousUnread = queryClient.getQueryData<number>([
        'portal',
        'notifications',
        'unread-count',
      ]);

      queryClient.setQueriesData<{ items: PortalNotification[]; total: number }>(
        { queryKey: ['portal', 'notifications'] },
        (current) => {
          if (!current?.items) return current;
          const now = new Date().toISOString();
          return {
            ...current,
            items: current.items.map((item) => (item.read_at ? item : { ...item, read_at: now })),
          };
        },
      );
      queryClient.setQueryData(['portal', 'notifications', 'unread-count'], 0);

      return { previousLists, previousUnread };
    },
    onError: (_error, _vars, context) => {
      context?.previousLists?.forEach(([key, data]) => {
        queryClient.setQueryData(key, data);
      });
      if (context?.previousUnread !== undefined) {
        queryClient.setQueryData(
          ['portal', 'notifications', 'unread-count'],
          context.previousUnread,
        );
      }
    },
    onSettled: async () => {
      await queryClient.invalidateQueries({ queryKey: ['portal', 'notifications'] });
    },
  });
}
