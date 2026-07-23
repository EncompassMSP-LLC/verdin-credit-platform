'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePortalCaseDetail, usePortalDocuments, usePrimaryCase } from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

export default function TimelinePage() {
  const { primary, data: cases, isLoading } = usePrimaryCase();
  const detailQuery = usePortalCaseDetail(primary?.id);
  const docsQuery = usePortalDocuments(primary?.id);

  const events = [
    ...(cases ?? []).map((item) => ({
      id: `case-${item.id}`,
      date: item.updated_at,
      title: `Case stage: ${item.stage.replaceAll('_', ' ')}`,
      detail: `${item.title} · ${item.status}`,
      type: 'case' as const,
    })),
    ...(docsQuery.data ?? []).map((doc) => ({
      id: `doc-${doc.id}`,
      date: doc.created_at,
      title: 'Document uploaded',
      detail: doc.title,
      type: 'document' as const,
    })),
  ].sort((a, b) => +new Date(b.date) - +new Date(a.date));

  return (
    <div>
      <PageHeader
        eyebrow="Credit Timeline"
        title="Platform activity timeline"
        description="Case updates and document events from your linked client record."
      />

      <div className="grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <PortalCard title="Timeline">
          {isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : !events.length ? (
            <p className="text-sm text-slate-500">No timeline events yet.</p>
          ) : (
            <ol className="relative space-y-0 border-l border-gold-500/40 pl-6">
              {events.map((event) => (
                <li key={event.id} className="relative pb-8 last:pb-0">
                  <span className="absolute -left-[1.64rem] top-1.5 h-3 w-3 rounded-full border-2 border-gold-500 bg-white dark:bg-navy-800" />
                  <p className="text-xs uppercase tracking-eyebrow text-slate-500">
                    {formatDate(event.date)} · {event.type}
                  </p>
                  <h3 className="mt-1 font-semibold">{event.title}</h3>
                  <p className="mt-1 text-sm text-slate-500 dark:text-white/65">{event.detail}</p>
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
            </dl>
          ) : (
            <p className="text-sm text-slate-500">Select/link a case to see detail.</p>
          )}
        </PortalCard>
      </div>
    </div>
  );
}
