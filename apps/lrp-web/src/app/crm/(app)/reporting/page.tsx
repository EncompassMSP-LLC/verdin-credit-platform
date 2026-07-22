'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { reporting } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';
import { cn } from '@/lib/utils';

export default function CrmReportingPage() {
  return (
    <RoleGate
      permission="reporting.view"
      fallback={<p className="text-sm text-slate-500">No access to reporting.</p>}
    >
      <PageHeader
        eyebrow="Insights"
        title="Reporting"
        description={`${reporting.periodLabel}. Partner funnel metrics—complementary to Reporting Center ops analytics.`}
      />

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {reporting.metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800"
          >
            <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-slate-500">
              {m.label}
            </p>
            <p className="mt-2 text-3xl font-semibold">{m.value}</p>
            <p
              className={cn(
                'mt-1 text-xs font-medium',
                m.tone === 'up' && 'text-emerald-700 dark:text-emerald-400',
                m.tone === 'down' && 'text-critical',
                m.tone === 'flat' && 'text-slate-500',
              )}
            >
              {m.delta}
            </p>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-4 lg:grid-cols-2">
        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
          <h2 className="text-sm font-semibold">Referral by source</h2>
          <table className="mt-3 w-full text-left text-sm">
            <thead>
              <tr className="text-[0.65rem] uppercase tracking-wider text-slate-500">
                <th className="py-2">Source</th>
                <th>Count</th>
                <th>Converted</th>
              </tr>
            </thead>
            <tbody>
              {reporting.referralBySource.map((row) => (
                <tr key={row.source} className="border-t border-navy-900/8 dark:border-white/10">
                  <td className="py-2.5 font-medium">{row.source}</td>
                  <td>{row.count}</td>
                  <td>{row.converted}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
          <h2 className="text-sm font-semibold">Partner leaderboard</h2>
          <table className="mt-3 w-full text-left text-sm">
            <thead>
              <tr className="text-[0.65rem] uppercase tracking-wider text-slate-500">
                <th className="py-2">Partner</th>
                <th>Referrals</th>
                <th>Funded YTD</th>
              </tr>
            </thead>
            <tbody>
              {reporting.partnerLeaderboard.map((row) => (
                <tr key={row.partner} className="border-t border-navy-900/8 dark:border-white/10">
                  <td className="py-2.5 font-medium">{row.partner}</td>
                  <td>{row.referrals}</td>
                  <td>{row.funded}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>

      <section className="mt-4 rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
        <h2 className="text-sm font-semibold">Funnel</h2>
        <ul className="mt-3 flex flex-wrap gap-2">
          {reporting.funnel.map((row) => (
            <li
              key={row.stage}
              className="rounded-md bg-sand-100 px-3 py-2 text-sm dark:bg-white/10"
            >
              <span className="font-medium">{STAGE_LABELS[row.stage]}</span>
              <span className="ml-2 text-slate-500">{row.count}</span>
            </li>
          ))}
        </ul>
      </section>
    </RoleGate>
  );
}
