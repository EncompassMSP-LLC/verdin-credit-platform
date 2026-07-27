'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import {
  usePortalCaseDetail,
  usePortalTimeline,
  usePrimaryCase,
  type PortalTimelineEventType,
} from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

const FILTERS: Array<{ id: 'all' | PortalTimelineEventType; label: string }> = [
  { id: 'all', label: 'All' },
  { id: 'readiness', label: 'Readiness' },
  { id: 'document', label: 'Documents' },
  { id: 'task', label: 'Tasks' },
  { id: 'case', label: 'Case' },
];

export default function TimelinePage() {
  const { primary, isLoading: casesLoading } = usePrimaryCase();
  const [filter, setFilter] = useState<'all' | PortalTimelineEventType>('all');
  const timelineQuery = usePortalTimeline(primary?.id, filter);
  const detailQuery = usePortalCaseDetail(primary?.id);
  const events = timelineQuery.data ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Credit Timeline"
        title="Your readiness timeline"
        description="Borrower-safe milestones: case progress, published readiness updates, document uploads, and completed action-plan tasks."
      />

      <div className="mb-4 flex flex-wrap gap-2">
        {FILTERS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setFilter(item.id)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
              filter === item.id
                ? 'bg-navy-800 text-white dark:bg-gold-500 dark:text-navy-950'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-white/10 dark:text-white/80'
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <PortalCard title="Timeline">
          {casesLoading || timelineQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : !primary ? (
            <p className="text-sm text-slate-500">Link a case to see your readiness timeline.</p>
          ) : !events.length ? (
            <p className="text-sm text-slate-500">No timeline events yet for this filter.</p>
          ) : (
            <ol className="relative space-y-0 border-l border-gold-500/40 pl-6">
              {events.map((event) => (
                <li key={event.id} className="relative pb-8 last:pb-0">
                  <span className="absolute -left-[1.64rem] top-1.5 h-3 w-3 rounded-full border-2 border-gold-500 bg-white dark:bg-navy-800" />
                  <p className="text-xs uppercase tracking-eyebrow text-slate-500">
                    {formatDate(event.event_at)} · {event.event_type}
                  </p>
                  <h3 className="mt-1 font-semibold">{event.title}</h3>
                  {event.detail ? (
                    <p className="mt-1 text-sm text-slate-500 dark:text-white/65">{event.detail}</p>
                  ) : null}
                  {event.href ? (
                    <Link
                      href={event.href}
                      className="mt-2 inline-block text-sm font-medium text-gold-700"
                    >
                      Open related view
                    </Link>
                  ) : null}
                </li>
              ))}
            </ol>
          )}
        </PortalCard>

        <PortalCard title="Primary case detail">
          {detailQuery.data ? (
            <dl className="space-y-3 text-sm">
              <div>
                <dt className="text-slate-500">Title</dt>
                <dd className="font-medium">{detailQuery.data.title}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Accounts</dt>
                <dd className="font-medium">{detailQuery.data.account_count}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Dispute accounts</dt>
                <dd className="mt-1 flex flex-wrap gap-2">
                  {Object.entries(detailQuery.data.dispute_accounts).length === 0 ? (
                    <span className="text-slate-500">None flagged</span>
                  ) : (
                    Object.entries(detailQuery.data.dispute_accounts).map(([key, value]) => (
                      <StatusPill key={key} tone="info">
                        {key}: {value}
                      </StatusPill>
                    ))
                  )}
                </dd>
              </div>
              <div className="flex flex-wrap gap-3 pt-2">
                <Link href="/portal/reports" className="text-sm font-medium text-gold-700">
                  Readiness report
                </Link>
                <Link href="/portal/tasks" className="text-sm font-medium text-gold-700">
                  Action plan
                </Link>
                <Link href="/portal/documents" className="text-sm font-medium text-gold-700">
                  Documents
                </Link>
              </div>
            </dl>
          ) : (
            <p className="text-sm text-slate-500">Select/link a case to see detail.</p>
          )}
        </PortalCard>
      </div>
    </div>
  );
}
