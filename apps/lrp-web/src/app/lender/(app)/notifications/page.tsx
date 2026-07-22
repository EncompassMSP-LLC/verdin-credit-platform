'use client';

import Link from 'next/link';
import { useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { notifications as seedNotifications } from '@/lib/lender/data';
import type { LenderNotification } from '@/lib/lender/types';
import { cn, formatDate } from '@/lib/utils';

export default function NotificationsPage() {
  const [items, setItems] = useState<LenderNotification[]>(seedNotifications);

  function markRead(id: string) {
    setItems((prev) => prev.map((n) => (n.id === id ? { ...n, read: true } : n)));
  }

  function markAllRead() {
    setItems((prev) => prev.map((n) => ({ ...n, read: true })));
  }

  const unread = items.filter((n) => !n.read).length;

  return (
    <RoleGate permission="notifications.view">
      <div>
        <PageHeader
          eyebrow="Notifications"
          title="Partner alerts"
          description={`${unread} unread. Local demo state—connects to platform notifications when Mortgage Partner APIs ship.`}
          actions={
            unread > 0 ? (
              <button
                type="button"
                onClick={markAllRead}
                className="rounded-md border border-navy-900/15 px-3 py-2 text-sm font-medium hover:border-gold-500/50 dark:border-white/15"
              >
                Mark all read
              </button>
            ) : null
          }
        />

        <PortalCard title="Inbox">
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
                      onClick={() => markRead(item.id)}
                      className="rounded-md bg-navy-900 px-3 py-1.5 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
                    >
                      Mark read
                    </button>
                  ) : null}
                </div>
              </li>
            ))}
          </ul>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
