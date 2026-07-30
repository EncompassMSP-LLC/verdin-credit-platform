'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import {
  categoryLabel,
  safePortalHref,
  useMarkAllPortalNotificationsRead,
  useMarkPortalNotificationRead,
  usePortalNotifications,
} from '@/lib/portal/notification-hooks';
import { cn, formatDate } from '@/lib/utils';

/**
 * Spec: Vol 19 · borrower notifications inbox
 * Live: GET/POST /portal/notifications* (LRP-302A)
 */
export default function NotificationsPage() {
  const liveQuery = usePortalNotifications();
  const markRead = useMarkPortalNotificationRead();
  const markAll = useMarkAllPortalNotificationsRead();

  const items = liveQuery.data?.items ?? [];
  const unread = items.filter((n) => !n.read_at).length;

  return (
    <div>
      <PageHeader
        eyebrow="Notifications"
        title="Your alerts"
        description={
          liveQuery.isLoading
            ? 'Loading your notification feed…'
            : `${unread} unread · newest first · advisory platform updates only.`
        }
        actions={
          unread > 0 ? (
            <button
              type="button"
              onClick={() => markAll.mutate()}
              disabled={markAll.isPending}
              className="rounded-md border border-navy-900/15 px-3 py-2 text-sm font-medium hover:border-gold-500/50 disabled:opacity-60 dark:border-white/15"
            >
              {markAll.isPending ? 'Updating…' : 'Mark all read'}
            </button>
          ) : null
        }
      />

      <PortalCard title="Inbox">
        {liveQuery.isLoading ? (
          <p className="text-sm text-slate-500">Loading notifications…</p>
        ) : null}
        {liveQuery.isError ? (
          <p className="text-sm text-red-700" role="alert">
            Could not load notifications. Try again in a moment.
          </p>
        ) : null}
        {!liveQuery.isLoading && !liveQuery.isError && items.length === 0 ? (
          <p className="text-sm text-slate-500">
            No notifications yet. Updates about documents, tasks, and readiness will appear here.
          </p>
        ) : null}
        {!liveQuery.isLoading && !liveQuery.isError && items.length > 0 ? (
          <ul className="divide-y divide-navy-900/8 dark:divide-white/10">
            {items.map((item) => {
              const href = safePortalHref(item.action_url);
              const isUnread = !item.read_at;
              return (
                <li
                  key={item.id}
                  className={cn(
                    'flex flex-col gap-3 py-4 sm:flex-row sm:items-start sm:justify-between',
                    isUnread && 'bg-gold-500/[0.04]',
                  )}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-navy-900 dark:text-white">{item.title}</p>
                      <StatusPill tone="info">{categoryLabel(item.category)}</StatusPill>
                      {isUnread ? (
                        <span className="text-[0.65rem] font-semibold uppercase text-gold-700 dark:text-gold-400">
                          Unread
                        </span>
                      ) : null}
                    </div>
                    {item.body ? (
                      <p className="mt-1 text-sm text-slate-600 dark:text-white/70">{item.body}</p>
                    ) : null}
                    <p className="mt-2 text-xs text-slate-400">
                      {formatDate(item.created_at, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <Link
                      href={href}
                      className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:border-gold-500/50 dark:border-white/15"
                    >
                      Open
                    </Link>
                    {isUnread ? (
                      <button
                        type="button"
                        onClick={() => markRead.mutate(item.id)}
                        disabled={markRead.isPending}
                        className="rounded-md bg-navy-900 px-3 py-1.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60 dark:bg-gold-500 dark:text-navy-900"
                      >
                        Mark read
                      </button>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ul>
        ) : null}
        {liveQuery.data && liveQuery.data.pages > 1 ? (
          <p className="mt-4 text-xs text-slate-400">
            Showing page {liveQuery.data.page} of {liveQuery.data.pages} ({liveQuery.data.total}{' '}
            total)
          </p>
        ) : null}
      </PortalCard>
    </div>
  );
}
