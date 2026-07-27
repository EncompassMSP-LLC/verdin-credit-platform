'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { useLenderAuth } from '@/lib/lender/auth';
import { notifications as seedNotifications } from '@/lib/lender/data';
import {
  useLenderNotifications,
  useMarkAllLenderNotificationsRead,
  useMarkLenderNotificationRead,
} from '@/lib/lender/notification-hooks';
import type { LenderNotification } from '@/lib/lender/types';
import { cn, formatDate } from '@/lib/utils';

/**
 * Spec: Vol 20 · partner notifications inbox
 * Live: platform GET/POST /notifications (LRP-105). Demo seed retained for local demo auth.
 */
export default function NotificationsPage() {
  const { authMode } = useLenderAuth();
  const isDemo = authMode === 'demo';
  const [demoItems, setDemoItems] = useState<LenderNotification[]>(seedNotifications);

  const liveQuery = useLenderNotifications();
  const markRead = useMarkLenderNotificationRead();
  const markAll = useMarkAllLenderNotificationsRead();

  const items = useMemo(
    () => (isDemo ? demoItems : (liveQuery.data ?? [])),
    [demoItems, isDemo, liveQuery.data],
  );
  const unread = items.filter((n) => !n.read).length;

  function onMarkRead(id: string) {
    if (isDemo) {
      setDemoItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
      return;
    }
    markRead.mutate(id);
  }

  function onMarkAllRead() {
    if (isDemo) {
      setDemoItems((prev) => prev.map((n) => ({ ...n, read: true })));
      return;
    }
    markAll.mutate();
  }

  return (
    <RoleGate permission="notifications.view">
      <div>
        <PageHeader
          eyebrow="Notifications"
          title="Partner alerts"
          description={
            isDemo
              ? `${unread} unread. Demo inbox — switch to platform auth for live notifications.`
              : `${unread} unread from the platform notifications module.`
          }
          actions={
            unread > 0 ? (
              <button
                type="button"
                onClick={onMarkAllRead}
                disabled={!isDemo && markAll.isPending}
                className="rounded-md border border-navy-900/15 px-3 py-2 text-sm font-medium hover:border-gold-500/50 disabled:opacity-60 dark:border-white/15"
              >
                {!isDemo && markAll.isPending ? 'Updating…' : 'Mark all read'}
              </button>
            ) : null
          }
        />

        <PortalCard title="Inbox">
          {!isDemo && liveQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading notifications…</p>
          ) : null}
          {!isDemo && liveQuery.isError ? (
            <p className="text-sm text-red-700">Could not load platform notifications.</p>
          ) : null}
          {(isDemo || (!liveQuery.isLoading && !liveQuery.isError)) && items.length === 0 ? (
            <p className="text-sm text-slate-500">No notifications yet.</p>
          ) : null}
          {(isDemo || (!liveQuery.isLoading && !liveQuery.isError)) && items.length > 0 ? (
            <ul className="divide-y divide-navy-900/8 dark:divide-white/10">
              {items.map((item) => (
                <li
                  key={item.id}
                  className={cn(
                    'flex flex-col gap-3 py-4 sm:flex-row sm:items-start sm:justify-between',
                    !item.read && 'bg-gold-500/[0.04]',
                  )}
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <p className="font-medium text-navy-900 dark:text-white">{item.title}</p>
                      <StatusPill
                        tone={
                          item.severity === 'warn'
                            ? 'warn'
                            : item.severity === 'success'
                              ? 'good'
                              : 'info'
                        }
                      >
                        {item.severity}
                      </StatusPill>
                      {!item.read ? (
                        <span className="text-[0.65rem] font-semibold uppercase text-gold-700 dark:text-gold-400">
                          Unread
                        </span>
                      ) : null}
                    </div>
                    <p className="mt-1 text-sm text-slate-600 dark:text-white/70">{item.body}</p>
                    <p className="mt-2 text-xs text-slate-400">
                      {formatDate(item.at, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <Link
                      href={item.href}
                      className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:border-gold-500/50 dark:border-white/15"
                    >
                      Open
                    </Link>
                    {!item.read ? (
                      <button
                        type="button"
                        onClick={() => onMarkRead(item.id)}
                        disabled={!isDemo && markRead.isPending}
                        className="rounded-md bg-navy-900 px-3 py-1.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60 dark:bg-gold-500 dark:text-navy-900"
                      >
                        Mark read
                      </button>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          ) : null}
        </PortalCard>
      </div>
    </RoleGate>
  );
}
