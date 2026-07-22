'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatTile, StatusPill } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { borrowers, readinessReports } from '@/lib/lender/data';
import { STAGE_LABELS } from '@/lib/lender/nav';
import { formatDate } from '@/lib/utils';

/**
 * Lender view of AI credit analysis outputs.
 * Seeded from partner cohort until ENABLE_MORTGAGE_PARTNER wires staff runs to lenders.
 */
export default function LenderAnalysisPage() {
  const ready = readinessReports.filter((r) => r.overall >= 70);
  const avg =
    readinessReports.length === 0
      ? 0
      : Math.round(
          readinessReports.reduce((sum, r) => sum + r.overall, 0) / readinessReports.length,
        );

  return (
    <RoleGate permission="readiness.view">
      <div>
        <PageHeader
          eyebrow="AI Credit Analysis"
          title="Enterprise credit analysis for partner handoff"
          description="Borrower Readiness Score™, mortgage readiness, Metro 2 / FCRA / identity audits, utilization, collections, and dispute recommendations—advisory only, never an underwriting decision."
        />

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatTile label="Cohort avg readiness" value={`${avg}`} hint="Advisory composite" />
          <StatTile
            label="Near / lending ready"
            value={`${ready.length}`}
            hint={`${readinessReports.length} scored files`}
            tone="good"
          />
          <StatTile
            label="Active pipeline files"
            value={`${borrowers.filter((b) => !['funded', 'declined', 'withdrawn'].includes(b.stage)).length}`}
          />
          <StatTile label="Engine" value="Shared" hint="Parsers · Metro2 · FCRA · Intelligence" />
        </div>

        <PortalCard
          className="mt-6"
          title="Mortgage readiness reports"
          description="Generated from the shared platform analysis orchestrator once partner APIs are linked."
        >
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className="border-b border-navy-900/10 text-[0.65rem] uppercase tracking-wider text-slate-500">
                  <th className="px-3 py-2">Borrower</th>
                  <th className="px-3 py-2">Score</th>
                  <th className="px-3 py-2">Band</th>
                  <th className="px-3 py-2">Est. ready</th>
                  <th className="px-3 py-2">Stage</th>
                  <th className="px-3 py-2">Blockers</th>
                </tr>
              </thead>
              <tbody>
                {readinessReports.map((report) => {
                  const borrower = borrowers.find((b) => b.id === report.borrowerId);
                  return (
                    <tr key={report.id} className="border-b border-navy-900/8">
                      <td className="px-3 py-3 font-medium">{report.borrowerName}</td>
                      <td className="px-3 py-3 tabular-nums">{report.overall}</td>
                      <td className="px-3 py-3">
                        <StatusPill tone={report.overall >= 85 ? 'good' : 'info'}>
                          {report.band}
                        </StatusPill>
                      </td>
                      <td className="px-3 py-3">
                        {report.estimatedReadyDate ? formatDate(report.estimatedReadyDate) : 'TBD'}
                      </td>
                      <td className="px-3 py-3">{borrower ? STAGE_LABELS[borrower.stage] : '—'}</td>
                      <td className="px-3 py-3 text-slate-500">
                        {report.blockers.length || 'None'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </PortalCard>

        <PortalCard className="mt-6" title="Analysis packs included">
          <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 text-sm">
            {[
              'Upload / parse Equifax · Experian · TransUnion',
              'Tradeline extraction',
              'Metro 2 audit',
              'FCRA audit',
              'Identity theft indicators',
              'Utilization analysis',
              'Late payment review',
              'Collection analysis',
              'Charge-off review',
              'Public records',
              'Inquiry analysis',
              'Borrower Readiness Score™',
              'Mortgage Readiness Report + PDF export',
              'Lender Summary · Action Plan · Dispute Recommendations · Timeline',
            ].map((item) => (
              <li
                key={item}
                className="rounded-md border border-navy-900/8 bg-[#F8FAFC] px-3 py-2 dark:border-white/10 dark:bg-navy-900/40"
              >
                {item}
              </li>
            ))}
          </ul>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
