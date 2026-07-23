'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatTile, StatusPill } from '@/components/portal/PortalCard';
import { usePlatformAuth } from '@/lib/platform/auth';
import { usePortalCases, usePortalDocuments, usePortalMessages } from '@/lib/platform/hooks';
import { usePortalInsights, usePortalReadiness } from '@/lib/platform/readiness-hooks';
import { formatDate } from '@/lib/utils';

const stageLabel: Record<string, string> = {
  intake: 'Intake',
  review: 'Review',
  evidence_gathering: 'Evidence gathering',
  dispute_preparation: 'Dispute preparation',
  awaiting_response: 'Awaiting response',
  monitoring: 'Monitoring',
  complete: 'Complete',
};

export default function DashboardPage() {
  const { user } = usePlatformAuth();
  const casesQuery = usePortalCases();
  const primary = casesQuery.data?.[0];
  const docsQuery = usePortalDocuments(primary?.id);
  const messagesQuery = usePortalMessages(primary?.id);
  const readinessQuery = usePortalReadiness(primary?.id);
  const insightsQuery = usePortalInsights(primary?.id);

  const firstName =
    user?.client_display_name?.split(' ')[0] || user?.email?.split('@')[0] || 'there';
  const unreadStaff =
    messagesQuery.data?.messages.filter((m) => m.sender_role === 'staff').length ?? 0;
  const readiness = readinessQuery.data;
  const topInsight = insightsQuery.data?.items[0];

  return (
    <div>
      <PageHeader
        eyebrow="Dashboard"
        title={`Welcome back, ${firstName}`}
        description="Live data from the Ultimate Credit Repair platform—cases, documents, messages, and readiness."
        actions={
          <Link
            href="/portal/documents"
            className="inline-flex rounded-brand bg-gold-500 px-4 py-2.5 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400"
          >
            Documents
          </Link>
        }
      />

      {casesQuery.isError ? (
        <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          Could not load cases from the platform API. Confirm the API is running and{' '}
          <code>ENABLE_CLIENT_PORTAL=true</code>.
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatTile
          label="Open cases"
          value={`${casesQuery.data?.length ?? '—'}`}
          hint={primary ? primary.title : 'No cases linked yet'}
        />
        <StatTile
          label="Primary stage"
          value={primary ? (stageLabel[primary.stage] ?? primary.stage) : '—'}
          hint={primary ? `Updated ${formatDate(primary.updated_at)}` : 'Awaiting case'}
        />
        <StatTile
          label="Documents"
          value={`${docsQuery.data?.length ?? '—'}`}
          hint="On primary case"
        />
        <StatTile
          label="Thread messages"
          value={`${messagesQuery.data?.messages.length ?? '—'}`}
          hint={unreadStaff ? `${unreadStaff} from staff` : 'Case messaging'}
        />
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <PortalCard
          title="Your cases"
          description="Pulled from /portal/cases on the shared database."
        >
          {casesQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading cases…</p>
          ) : !casesQuery.data?.length ? (
            <p className="text-sm text-slate-500">
              No portal-visible cases yet. Ask your advisor to link an active case to your client
              record.
            </p>
          ) : (
            <ul className="space-y-3">
              {casesQuery.data.map((item) => (
                <li
                  key={item.id}
                  className="rounded-brand border border-navy-900/8 bg-sand-50 p-4 dark:border-white/10 dark:bg-navy-900/40"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <p className="font-medium text-navy-900 dark:text-white">{item.title}</p>
                    <StatusPill tone="info">{stageLabel[item.stage] ?? item.stage}</StatusPill>
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {item.case_number ?? item.id.slice(0, 8)} · {item.status} · Updated{' '}
                    {formatDate(item.updated_at)}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </PortalCard>

        <PortalCard
          title="Readiness composite"
          description="Live from /portal/cases/{id}/readiness — advisory, not a funding guarantee."
        >
          {readinessQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading readiness…</p>
          ) : readiness ? (
            <>
              <p className="text-4xl font-semibold tabular-nums text-navy-900 dark:text-white">
                {readiness.overall}
              </p>
              <p className="mt-1 text-sm text-slate-500 dark:text-white/60">{readiness.band}</p>
              <p className="mt-4 text-sm font-medium text-navy-900 dark:text-white">
                {topInsight?.title ?? 'Review blockers and learning modules to keep momentum.'}
              </p>
              <Link
                href="/portal/readiness"
                className="mt-4 inline-block text-sm font-medium text-gold-700 dark:text-gold-400"
              >
                View readiness detail →
              </Link>
            </>
          ) : (
            <p className="text-sm text-slate-500 dark:text-white/65">
              {primary
                ? 'Readiness will appear once your case is available.'
                : 'Link a case to unlock readiness.'}
            </p>
          )}
        </PortalCard>
      </div>
    </div>
  );
}
