'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { usePlatformAuth } from '@/lib/platform/auth';
import { usePortalCases, usePortalDocuments, usePortalMessages } from '@/lib/platform/hooks';
import {
  usePortalChecklist,
  usePortalInsights,
  usePortalLearningModules,
  usePortalReadiness,
} from '@/lib/platform/readiness-hooks';
import {
  caseStageLabel,
  readinessBandClass,
  readinessBandLabel,
} from '@/lib/portal/readiness-display';
import { formatDate } from '@/lib/utils';

/**
 * Spec: Vol 19 · pages/dashboard.md (ready-for-build / E2)
 * Band-first readiness; partner name when present; next tasks + progress.
 */
export default function DashboardPage() {
  const { user } = usePlatformAuth();
  const casesQuery = usePortalCases();
  const primary = casesQuery.data?.[0];
  const docsQuery = usePortalDocuments(primary?.id);
  const messagesQuery = usePortalMessages(primary?.id);
  const readinessQuery = usePortalReadiness(primary?.id);
  const insightsQuery = usePortalInsights(primary?.id);
  const checklistQuery = usePortalChecklist(primary?.id);
  const learningQuery = usePortalLearningModules();

  const firstName =
    user?.client_display_name?.split(' ')[0] || user?.email?.split('@')[0] || 'there';
  const readiness = readinessQuery.data;
  const partnerName =
    (primary as { referring_partner_name?: string | null } | undefined)?.referring_partner_name ??
    null;

  const checklist = checklistQuery.data ?? [];
  const openTasks = checklist.filter((t) => t.status === 'open').slice(0, 3);
  const doneCount = checklist.filter((t) => t.status === 'done').length;
  const progressPct =
    checklist.length > 0 ? Math.round((doneCount / checklist.length) * 100) : null;

  const staffMessages =
    messagesQuery.data?.messages.filter((m) => m.sender_role === 'staff').length ?? 0;
  const nextLearning = learningQuery.data?.find((m) => !m.completed);

  return (
    <div>
      <PageHeader
        eyebrow="Dashboard"
        title={`Welcome back, ${firstName}`}
        description={ADVISORY_DISCLAIMER_SHORT}
        actions={
          <Link
            href="/portal/tasks"
            className="inline-flex rounded-brand bg-gold-500 px-4 py-2.5 text-sm font-semibold uppercase tracking-wide text-navy-900 hover:bg-gold-400"
          >
            View tasks
          </Link>
        }
      />

      {partnerName ? (
        <p className="mb-4 text-sm text-slate-600">
          Referred by <span className="font-medium text-navy-900">{partnerName}</span>
        </p>
      ) : null}

      {casesQuery.isError ? (
        <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          Could not load cases from the platform API. Confirm the API is running and{' '}
          <code>ENABLE_CLIENT_PORTAL=true</code>.
        </p>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <PortalCard
          title="Readiness"
          description="Advisory band from your linked case — not an underwriting decision."
        >
          {readinessQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading readiness…</p>
          ) : readiness ? (
            <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <span
                  className={`inline-flex rounded-brand px-3 py-1 text-sm font-semibold ${readinessBandClass(readiness.band)}`}
                >
                  {readinessBandLabel(readiness.band)}
                </span>
                <p className="mt-2 text-sm text-slate-500">
                  Updated {formatDate(readiness.updated_at)}
                  {primary ? ` · ${caseStageLabel(primary.stage)}` : null}
                </p>
                {insightsQuery.data?.items[0] ? (
                  <p className="mt-3 text-sm font-medium text-navy-900">
                    {insightsQuery.data.items[0].title}
                  </p>
                ) : null}
              </div>
              <Link
                href="/portal/readiness"
                className="inline-flex shrink-0 rounded-brand border border-lrp-border bg-lrp-surface-elevated px-4 py-2.5 text-sm font-semibold text-navy-900 hover:bg-lrp-surface"
              >
                View readiness
              </Link>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              {primary
                ? 'We’re preparing your readiness view — check back soon.'
                : 'Ask your advisor to link a case to unlock readiness.'}
            </p>
          )}
        </PortalCard>

        <PortalCard title="Progress" description="Checklist completion on your primary case.">
          {checklistQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : progressPct == null ? (
            <p className="text-sm text-slate-500">No checklist items yet.</p>
          ) : (
            <>
              <p className="text-3xl font-semibold tabular-nums text-navy-900">{progressPct}%</p>
              <div className="mt-3 h-2 overflow-hidden rounded-full bg-lrp-surface">
                <div
                  className="h-full rounded-full bg-progress-accent"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-slate-500">
                {doneCount} of {checklist.length} tasks complete · {docsQuery.data?.length ?? 0}{' '}
                documents on file
              </p>
            </>
          )}
        </PortalCard>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.3fr_1fr]">
        <PortalCard
          title="Next up"
          description="Top open tasks from your action plan."
          action={
            <Link href="/portal/tasks" className="text-sm font-medium text-gold-700">
              All tasks →
            </Link>
          }
        >
          {!primary ? (
            <p className="text-sm text-slate-500">Link a case to see tasks.</p>
          ) : checklistQuery.isLoading ? (
            <p className="text-sm text-slate-500">Loading tasks…</p>
          ) : openTasks.length === 0 ? (
            <p className="text-sm text-slate-500">
              No open tasks — nice work. Check learning next.
            </p>
          ) : (
            <ul className="space-y-3">
              {openTasks.map((task) => (
                <li
                  key={task.id}
                  className="rounded-brand border border-lrp-border bg-lrp-surface px-4 py-3"
                >
                  <p className="font-medium text-navy-900">{task.title}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {task.category}
                    {task.due_date ? ` · Due ${formatDate(task.due_date)}` : null}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </PortalCard>

        <div className="space-y-6">
          <PortalCard title="Messages" description="Staff updates on your case.">
            <p className="text-2xl font-semibold tabular-nums text-navy-900">
              {messagesQuery.isLoading ? '—' : staffMessages}
            </p>
            <p className="mt-1 text-sm text-slate-500">Messages from your team</p>
            <Link
              href="/portal/messages"
              className="mt-3 inline-block text-sm font-medium text-gold-700"
            >
              Open messages →
            </Link>
          </PortalCard>

          <PortalCard
            title="Keep learning"
            description="Short modules that support readiness habits."
          >
            {learningQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading modules…</p>
            ) : nextLearning ? (
              <>
                <p className="font-medium text-navy-900">{nextLearning.title}</p>
                <p className="mt-1 text-sm text-slate-500">{nextLearning.summary}</p>
                <Link
                  href="/portal/learning"
                  className="mt-3 inline-block text-sm font-medium text-gold-700"
                >
                  Continue learning →
                </Link>
              </>
            ) : (
              <>
                <p className="text-sm text-slate-500">You’re caught up on modules.</p>
                <Link
                  href="/portal/learning"
                  className="mt-3 inline-block text-sm font-medium text-gold-700"
                >
                  Learning center →
                </Link>
              </>
            )}
          </PortalCard>
        </div>
      </div>

      {casesQuery.data && casesQuery.data.length > 0 ? (
        <PortalCard
          className="mt-6"
          title="Your cases"
          description="Linked cases on the shared platform."
        >
          <ul className="space-y-3">
            {casesQuery.data.map((item) => (
              <li
                key={item.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-brand border border-lrp-border bg-lrp-surface px-4 py-3"
              >
                <div>
                  <p className="font-medium text-navy-900">{item.title}</p>
                  <p className="text-xs text-slate-500">
                    {item.case_number ?? item.id.slice(0, 8)} · Updated{' '}
                    {formatDate(item.updated_at)}
                  </p>
                </div>
                <StatusPill tone="info">{caseStageLabel(item.stage)}</StatusPill>
              </li>
            ))}
          </ul>
        </PortalCard>
      ) : null}
    </div>
  );
}
