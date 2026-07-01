import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getUnreadNotificationCount,
  listNotifications,
  markAllNotificationsRead,
  markNotificationRead,
} from '@verdin/api-client';
import { useState } from 'react';

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  const unreadQuery = useQuery({
    queryKey: ['notifications', 'unread-count'],
    queryFn: getUnreadNotificationCount,
    refetchInterval: 30_000,
  });

  const listQuery = useQuery({
    queryKey: ['notifications', 'list'],
    queryFn: () => listNotifications({ page_size: 10, sort_order: 'desc' }),
    enabled: open,
  });

  const markReadMutation = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const markAllMutation = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });

  const unreadCount = unreadQuery.data?.unread_count ?? 0;

  return (
    <div className="relative">
      <button
        type="button"
        aria-label="Notifications"
        onClick={() => setOpen((value) => !value)}
        className="relative rounded-md border border-brand-700 bg-brand-800 px-3 py-2 text-sm text-white hover:bg-brand-700"
      >
        Notifications
        {unreadCount > 0 ? (
          <span className="absolute -right-1 -top-1 inline-flex min-h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-xs font-semibold">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div className="absolute right-0 z-20 mt-2 w-80 rounded-md border border-gray-200 bg-white shadow-lg">
          <div className="flex items-center justify-between border-b px-4 py-3">
            <p className="text-sm font-semibold text-gray-900">Notifications</p>
            <button
              type="button"
              className="text-xs text-brand-700 hover:underline"
              onClick={() => markAllMutation.mutate()}
              disabled={unreadCount === 0 || markAllMutation.isPending}
            >
              Mark all read
            </button>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {listQuery.isLoading ? (
              <p className="px-4 py-3 text-sm text-gray-500">Loading…</p>
            ) : listQuery.data?.items.length ? (
              listQuery.data.items.map((notification) => (
                <button
                  key={notification.id}
                  type="button"
                  className={`block w-full border-b px-4 py-3 text-left hover:bg-gray-50 ${
                    notification.read_at ? 'opacity-70' : ''
                  }`}
                  onClick={() => {
                    if (!notification.read_at) {
                      markReadMutation.mutate(notification.id);
                    }
                  }}
                >
                  <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                  {notification.body ? (
                    <p className="mt-1 line-clamp-2 text-xs text-gray-600">{notification.body}</p>
                  ) : null}
                  <p className="mt-1 text-xs uppercase tracking-wide text-gray-400">
                    {notification.category}
                  </p>
                </button>
              ))
            ) : (
              <p className="px-4 py-6 text-sm text-gray-500">No notifications yet.</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}
