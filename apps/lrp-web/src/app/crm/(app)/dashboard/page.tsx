'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { borrowers, partners, referrals, tasks, reporting } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';

export default function CrmDashboardPage() {
  const openTasks = tasks.filter((t) => t.status === 'open' || t.status === 'in_progress').length;
  const activePartners = partners.filter((p) => p.status === 'active').length;
  const newReferrals = referrals.filter((r) => r.status === 'new').length;
  const nearReady = borrowers.filter((b) =>
    ['near_ready', 'mortgage_ready', 'in_underwriting'].includes(b.stage),
  ).length;

  return (
    <RoleGate
      permission="dashboard.view"
      fallback={<p className="text-sm text-slate-500">You do not have access to the dashboard.</p>}
    >
      <PageHeader
        eyebrow="Overview"
        title="CRM dashboard"
        description="Enterprise operating view across partners, borrowers, referrals, and readiness pipeline. Advisory signals only—not underwriting decisions."
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        {[
          { label: 'Active partners', value: String(activePartners), href: '/crm/partners' },
          { label: 'Borrowers in flight', value: String(borrowers.length), href: '/crm/borrowers' },
          { label: 'New referrals', value: String(newReferrals), href: '/crm/referrals' },
          { label: 'Open tasks', value: String(openTasks), href: '/crm/tasks' },
        ].map((card) => (
          <Link
            key={card.label}
            href={card.href}
            className="rounded-md border border-navy-900/10 bg-white p-4 transition hover:border-gold-500/50 dark:border-white/10 dark:bg-navy-800"
          >
            <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-slate-500 dark:text-white/50">
              {card.label}
            </p>
            <p className="mt-2 text-3xl font-semibold text-navy-900 dark:text-white">
              {card.value}
            </p>
          </Link>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-3">
        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800 lg:col-span-2">
          <h2 className="text-sm font-semibold">Pipeline snapshot</h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-white/55">
            {nearReady} borrowers at near-ready or beyond · {reporting.periodLabel}
          </p>
          <ul className="mt-4 space-y-2">
            {reporting.funnel.slice(0, 8).map((row) => (
              <li key={row.stage} className="flex items-center gap-3 text-sm">
                <span className="w-36 shrink-0 text-slate-600 dark:text-white/65">
                  {STAGE_LABELS[row.stage]}
                </span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-sand-100 dark:bg-white/10">
                  <div
                    className="h-full rounded-full bg-gold-500"
                    style={{ width: `${Math.min(100, row.count * 6)}%` }}
                  />
                </div>
                <span className="w-8 text-right font-medium">{row.count}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
          <h2 className="text-sm font-semibold">Quick links</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {[
              ['/crm/pipeline', 'Open pipeline board'],
              ['/crm/automations', 'Review automations'],
              ['/crm/reporting', 'Referral reporting'],
              ['/crm/permissions', 'Role permissions'],
            ].map(([href, label]) => (
              <li key={href}>
                <Link
                  href={href}
                  className="font-medium text-gold-700 hover:underline dark:text-gold-400"
                >
                  {label}
                </Link>
              </li>
            ))}
          </ul>
          <p className="mt-6 text-xs leading-relaxed text-slate-500 dark:text-white/50">
            Architecture: CRM UI edition on shared Verdin APIs (clients, tasks, documents,
            notifications). Partner/referral persistence ships with Mortgage Partner APIs.
          </p>
        </section>
      </div>
    </RoleGate>
  );
}
