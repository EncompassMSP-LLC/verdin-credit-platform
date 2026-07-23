'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePrimaryCase } from '@/lib/platform/hooks';
import { usePortalReadiness } from '@/lib/platform/readiness-hooks';
import { formatDate } from '@/lib/utils';

export default function ReadinessPage() {
  const { primary } = usePrimaryCase();
  const readinessQuery = usePortalReadiness(primary?.id);
  const readiness = readinessQuery.data;

  return (
    <div>
      <PageHeader
        eyebrow="Readiness Score"
        title="Lending readiness you can explain"
        description="A composite view of credit and file readiness—not a guarantee of approval. Built from your case tradeline intelligence."
      />

      {!primary ? (
        <p className="rounded-brand border border-navy-900/10 bg-sand-50 px-4 py-3 text-sm text-slate-600 dark:border-white/10 dark:bg-navy-900/40 dark:text-white/70">
          Link a case to your client record to view readiness.
        </p>
      ) : readinessQuery.isLoading ? (
        <p className="text-sm text-slate-500">Loading readiness…</p>
      ) : readinessQuery.isError ? (
        <p className="rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          Could not load readiness from the platform API.
        </p>
      ) : readiness ? (
        <>
          <p className="mb-4 text-xs text-slate-500 dark:text-white/55">{readiness.disclaimer}</p>

          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <PortalCard>
              <div className="flex flex-col items-center py-6 text-center">
                <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
                  Overall readiness
                </p>
                <p className="mt-3 text-6xl font-semibold tabular-nums text-navy-900 dark:text-white">
                  {readiness.overall}
                </p>
                <div className="mt-3">
                  <StatusPill tone="info">{readiness.band}</StatusPill>
                </div>
                <p className="mt-4 text-sm text-slate-500 dark:text-white/60">
                  {readiness.trend != null
                    ? `${readiness.trend > 0 ? '+' : ''}${readiness.trend} points since last calculation · `
                    : null}
                  Updated {formatDate(readiness.updated_at)}
                </p>
                <div className="mt-6 h-2 w-full max-w-xs overflow-hidden rounded-full bg-sand-200 dark:bg-navy-900">
                  <div
                    className="h-full rounded-full bg-progress-accent"
                    style={{ width: `${readiness.overall}%` }}
                  />
                </div>
              </div>
            </PortalCard>

            <PortalCard title="Dimension breakdown">
              <ul className="space-y-4">
                {readiness.dimensions.map((dimension) => (
                  <li key={dimension.key}>
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <span className="font-medium text-navy-900 dark:text-white">
                        {dimension.label}
                      </span>
                      <span className="tabular-nums text-slate-500">{dimension.score}</span>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-sand-200 dark:bg-navy-900">
                      <div
                        className="h-full rounded-full bg-navy-900 dark:bg-gold-500"
                        style={{ width: `${dimension.score}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </PortalCard>
          </div>

          <PortalCard
            className="mt-6"
            title="Current blockers"
            description="Resolve these with your advisor to advance toward lending ready."
          >
            {readiness.blockers.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-white/65">
                No high-priority blockers from current tradelines.
              </p>
            ) : (
              <div className="grid gap-4 md:grid-cols-3">
                {readiness.blockers.map((blocker) => (
                  <article
                    key={blocker.id}
                    className="rounded-brand border border-navy-900/8 bg-sand-50 p-4 dark:border-white/10 dark:bg-navy-900/40"
                  >
                    <StatusPill tone={blocker.impact === 'High' ? 'warn' : 'info'}>
                      {blocker.impact} impact
                    </StatusPill>
                    <h3 className="mt-3 font-semibold text-navy-900 dark:text-white">
                      {blocker.title}
                    </h3>
                    <p className="mt-2 text-sm text-slate-500 dark:text-white/65">
                      {blocker.action}
                    </p>
                  </article>
                ))}
              </div>
            )}
          </PortalCard>
        </>
      ) : null}
    </div>
  );
}
