'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatTile, StatusPill } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { DataTable } from '@/components/lender/DataTable';
import { useLenderAuth } from '@/lib/lender/auth';
import { analytics, borrowers, notifications } from '@/lib/lender/data';
import { STAGE_LABELS } from '@/lib/lender/nav';
import type { Borrower } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

export default function LenderDashboardPage() {
  const { user } = useLenderAuth();
  const nearReady = borrowers.filter((b) => ['near_ready', 'mortgage_ready'].includes(b.stage));
  const unread = notifications.filter((n) => !n.read);
  const activeBorrowers = borrowers.filter(
    (b) => !['declined', 'withdrawn', 'funded'].includes(b.stage),
  );

  return (
    <RoleGate permission="dashboard.view">
      <div>
        <PageHeader
          eyebrow="Dashboard"
          title={`Welcome, ${user?.displayName ?? 'partner'}`}
          description="Partner operations snapshot. Readiness scores are advisory composites for handoff—not credit scores, underwriting decisions, or funding guarantees."
          actions={
            <div className="flex flex-wrap gap-2">
              <Link
                href="/lender/pipeline"
                className="inline-flex rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm font-medium text-navy-900 hover:border-gold-500/50 dark:border-white/15 dark:bg-navy-800 dark:text-white"
              >
                Pipeline
              </Link>
              <Link
                href="/lender/referrals"
                className="inline-flex rounded-md bg-navy-900 px-3 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
              >
                Referrals
              </Link>
            </div>
          }
        />

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatTile
            label="Active borrowers"
            value={`${activeBorrowers.length}`}
            hint={`${borrowers.length} total in demo cohort`}
          />
          <StatTile
            label="Near / mortgage ready"
            value={`${nearReady.length}`}
            hint="Advisory readiness bands"
            tone="good"
          />
          <StatTile
            label="Referrals accepted (90d)"
            value={`${analytics.referralsAccepted}`}
            hint={analytics.periodLabel}
          />
          <StatTile
            label="Pull-through rate"
            value={`${Math.round(analytics.pullThroughRate * 100)}%`}
            hint={`${analytics.fundedCount} funded in period`}
          />
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatTile
            label="Avg days to near ready"
            value={`${analytics.avgDaysToNearReady}`}
            hint="Trailing operational metric"
          />
          <StatTile
            label="Mortgage-ready count"
            value={`${analytics.mortgageReadyCount}`}
            hint="Eligible for UW handoff review"
            tone="good"
          />
          <StatTile
            label="Unread notifications"
            value={`${unread.length}`}
            hint="Partner alerts"
            tone={unread.length ? 'warn' : 'default'}
          />
          <StatTile
            label="New referrals"
            value={`${borrowers.filter((b) => b.stage === 'referred').length}`}
            hint="Awaiting intake"
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.4fr_1fr]">
          <PortalCard
            title="Near-ready borrowers"
            description="Files approaching lending-ready advisory band. Confirm blockers with CRO before underwriting handoff."
            action={
              <Link
                href="/lender/borrowers"
                className="text-sm font-medium text-gold-700 dark:text-gold-400"
              >
                All borrowers →
              </Link>
            }
          >
            <DataTable<Borrower>
              rows={nearReady}
              empty="No near-ready borrowers in the demo cohort."
              onRowClick={(row) => {
                window.location.href = `/lender/borrowers/${row.id}`;
              }}
              columns={[
                {
                  key: 'name',
                  header: 'Borrower',
                  cell: (row) => (
                    <span className="font-medium text-navy-900 dark:text-white">
                      {row.displayName}
                    </span>
                  ),
                },
                {
                  key: 'stage',
                  header: 'Stage',
                  cell: (row) => (
                    <StatusPill tone={row.stage === 'mortgage_ready' ? 'good' : 'info'}>
                      {STAGE_LABELS[row.stage] ?? row.stage}
                    </StatusPill>
                  ),
                },
                {
                  key: 'score',
                  header: 'Readiness',
                  cell: (row) => (
                    <span className="tabular-nums font-medium">{row.readinessScore}</span>
                  ),
                },
                {
                  key: 'ready',
                  header: 'Est. ready',
                  cell: (row) =>
                    row.estimatedReadyDate ? formatDate(row.estimatedReadyDate) : '—',
                },
              ]}
            />
          </PortalCard>

          <PortalCard
            title="Unread notifications"
            description="Recent partner alerts requiring review."
            action={
              <Link
                href="/lender/notifications"
                className="text-sm font-medium text-gold-700 dark:text-gold-400"
              >
                View all →
              </Link>
            }
          >
            {unread.length === 0 ? (
              <p className="text-sm text-slate-500">No unread notifications.</p>
            ) : (
              <ul className="space-y-3">
                {unread.slice(0, 5).map((item) => (
                  <li key={item.id}>
                    <Link
                      href={item.href}
                      className="block rounded-md border border-navy-900/8 bg-[#F8FAFC] p-3 transition hover:border-gold-500/40 dark:border-white/10 dark:bg-navy-900/40"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-medium text-navy-900 dark:text-white">
                          {item.title}
                        </p>
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
                      </div>
                      <p className="mt-1 text-xs text-slate-500">{item.body}</p>
                      <p className="mt-2 text-[0.65rem] text-slate-400">
                        {formatDate(item.at, {
                          month: 'short',
                          day: 'numeric',
                          hour: 'numeric',
                          minute: '2-digit',
                        })}
                      </p>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </PortalCard>
        </div>

        <PortalCard
          className="mt-6"
          title="Quick links"
          description="Jump to operational surfaces. Readiness exports remain advisory and staff-mediated on the CRO platform."
        >
          <div className="flex flex-wrap gap-2">
            {[
              { href: '/lender/readiness', label: 'Readiness reports' },
              { href: '/lender/pipeline', label: 'Pipeline board' },
              { href: '/lender/messages', label: 'Messages' },
              { href: '/lender/analytics', label: 'Analytics' },
            ].map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="inline-flex rounded-md border border-navy-900/10 bg-[#F8FAFC] px-3 py-2 text-sm font-medium text-navy-900 hover:border-gold-500/50 dark:border-white/10 dark:bg-navy-900/40 dark:text-white"
              >
                {link.label}
              </Link>
            ))}
          </div>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
