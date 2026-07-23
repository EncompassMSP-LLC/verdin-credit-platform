'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { usePrimaryCase } from '@/lib/platform/hooks';
import { usePortalReadiness } from '@/lib/platform/readiness-hooks';
import { readinessBandClass, readinessBandLabel } from '@/lib/portal/readiness-display';
import { formatDate } from '@/lib/utils';

/**
 * Spec: Vol 19 · pages/readiness-score.md + FOUNDER-REVIEW P0-1
 * Borrower v1 is band-only; numeric score is not shown to borrowers.
 */
export default function ReadinessPage() {
  const { primary } = usePrimaryCase();
  const readinessQuery = usePortalReadiness(primary?.id);
  const readiness = readinessQuery.data;

  return (
    <div>
      <PageHeader
        eyebrow="Readiness Score"
        title="Your Lending Readiness"
        description={ADVISORY_DISCLAIMER_SHORT}
      />

      {!primary ? (
        <p className="rounded-brand border border-lrp-border bg-lrp-surface px-4 py-3 text-sm text-slate-600">
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
          <p className="mb-4 text-xs leading-relaxed text-slate-500">{ADVISORY_DISCLAIMER_LONG}</p>

          <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <PortalCard>
              <div className="flex flex-col items-center py-8 text-center">
                <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">
                  Lending Readiness Score™
                </p>
                <span
                  className={`mt-4 inline-flex rounded-brand px-4 py-2 text-2xl font-semibold ${readinessBandClass(readiness.band)}`}
                >
                  {readinessBandLabel(readiness.band)}
                </span>
                <p className="mt-4 max-w-sm text-sm text-slate-500">
                  This band summarizes where you are in the readiness journey. It is not a FICO
                  score and not a loan decision.
                </p>
                <p className="mt-3 text-xs text-slate-500">
                  Updated {formatDate(readiness.updated_at)}
                </p>
                <Link
                  href="/portal/tasks"
                  className="mt-6 inline-flex rounded-brand bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700"
                >
                  Work on my plan
                </Link>
              </div>
            </PortalCard>

            <PortalCard
              title="What drives this band"
              description="High-level factors from your file. Details stay with your advisor."
            >
              <ul className="space-y-4">
                {readiness.dimensions.map((dimension) => (
                  <li key={dimension.key}>
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <span className="font-medium text-navy-900">{dimension.label}</span>
                      <StatusPill tone="info">
                        {dimension.score >= 70
                          ? 'On track'
                          : dimension.score >= 40
                            ? 'Needs attention'
                            : 'Priority'}
                      </StatusPill>
                    </div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-lrp-surface">
                      <div
                        className="h-full rounded-full bg-navy-900"
                        style={{ width: `${Math.min(100, Math.max(0, dimension.score))}%` }}
                        aria-hidden
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
            description="Resolve these with your advisor to move toward Lending Ready."
            action={
              <Link href="/portal/tasks" className="text-sm font-medium text-gold-700">
                Open tasks →
              </Link>
            }
          >
            {readiness.blockers.length === 0 ? (
              <p className="text-sm text-slate-500">
                No high-priority blockers from current tradelines.
              </p>
            ) : (
              <div className="grid gap-4 md:grid-cols-3">
                {readiness.blockers.map((blocker) => (
                  <article
                    key={blocker.id}
                    className="rounded-brand border border-lrp-border bg-lrp-surface p-4"
                  >
                    <p className="font-medium text-navy-900">{blocker.title}</p>
                    <p className="mt-2 text-sm text-slate-500">{blocker.impact}</p>
                    <p className="mt-2 text-xs font-medium text-gold-700">{blocker.action}</p>
                  </article>
                ))}
              </div>
            )}
          </PortalCard>

          <p className="mt-6 text-center text-sm">
            <Link href="/portal/reports" className="font-medium text-gold-700">
              View report summaries →
            </Link>
          </p>
        </>
      ) : (
        <p className="rounded-brand border border-lrp-border bg-lrp-surface px-4 py-3 text-sm text-slate-600">
          Analysis in progress — we’ll notify you when your readiness band is ready.
        </p>
      )}
    </div>
  );
}
