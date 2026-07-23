'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { usePortalDocuments, usePortalMessages, usePrimaryCase } from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

export default function NotificationsPage() {
  const { primary } = usePrimaryCase();
  const docsQuery = usePortalDocuments(primary?.id);
  const messagesQuery = usePortalMessages(primary?.id);

  const items = [
    ...(messagesQuery.data?.messages.slice(-5).reverse() ?? []).map((message) => ({
      id: `msg-${message.id}`,
      title: message.sender_role === 'staff' ? 'Staff message' : 'Your message sent',
      body: message.body,
      at: message.created_at,
      href: '/portal/messages',
    })),
    ...(docsQuery.data?.slice(0, 5) ?? []).map((doc) => ({
      id: `doc-${doc.id}`,
      title: 'Document on file',
      body: `${doc.title} · ${doc.processing_status}`,
      at: doc.created_at,
      href: '/portal/documents',
    })),
  ].sort((a, b) => +new Date(b.at) - +new Date(a.at));

  return (
    <div>
      <PageHeader
        eyebrow="Notifications"
        title="Recent platform activity"
        description="Derived from case messages and documents until a dedicated notifications feed is exposed on the portal API."
      />

      <PortalCard>
        {!primary ? (
          <p className="text-sm text-slate-500">No case linked yet.</p>
        ) : !items.length ? (
          <p className="text-sm text-slate-500">No recent activity.</p>
        ) : (
          <ul className="divide-y divide-navy-900/8 dark:divide-white/10">
            {items.map((item) => (
              <li key={item.id}>
                <Link
                  href={item.href}
                  className="flex items-start gap-3 py-4 transition hover:bg-sand-50 dark:hover:bg-navy-900/40"
                >
                  <span className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full bg-gold-500" />
                  <div>
                    <p className="font-medium">{item.title}</p>
                    <p className="text-sm text-slate-500 dark:text-white/65">{item.body}</p>
                    <p className="mt-1 text-xs text-slate-400">
                      {formatDate(item.at, {
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </PortalCard>
    </div>
  );
}
