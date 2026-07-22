'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { borrowers, pipelineCards, readinessReports, referrals } from '@/lib/lender/data';
import { exportRowsAsCsv } from '@/lib/lender/export';
import { STAGE_LABELS } from '@/lib/lender/nav';

export default function ExportsPage() {
  return (
    <RoleGate permission="reports.export">
      <div>
        <PageHeader
          eyebrow="Export center"
          title="Partner data exports"
          description="Download CSV extracts for operational review. Exports contain advisory readiness data—not underwriting approvals."
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <PortalCard
            title="Borrowers CSV"
            description="Cohort tracking with stage and advisory readiness."
          >
            <button
              type="button"
              onClick={() =>
                exportRowsAsCsv(
                  'lrp-borrowers.csv',
                  ['Name', 'Email', 'Stage', 'Readiness', 'Band', 'Est. ready', 'Progress'],
                  borrowers.map((b) => [
                    b.displayName,
                    b.email,
                    STAGE_LABELS[b.stage] ?? b.stage,
                    b.readinessScore,
                    b.readinessBand,
                    b.estimatedReadyDate,
                    `${b.progressPct}%`,
                  ]),
                )
              }
              className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
            >
              Export borrowers
            </button>
          </PortalCard>

          <PortalCard title="Referrals CSV" description="Referral queue with status and product.">
            <button
              type="button"
              onClick={() =>
                exportRowsAsCsv(
                  'lrp-referrals.csv',
                  ['Borrower', 'Email', 'Source', 'Status', 'Product', 'Referred'],
                  referrals.map((r) => [
                    r.borrowerName,
                    r.borrowerEmail,
                    r.source,
                    r.status,
                    r.targetProduct,
                    r.referredAt,
                  ]),
                )
              }
              className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
            >
              Export referrals
            </button>
          </PortalCard>

          <PortalCard title="Readiness CSV" description="Advisory readiness reports with blockers.">
            <button
              type="button"
              onClick={() =>
                exportRowsAsCsv(
                  'lrp-readiness.csv',
                  ['Borrower', 'Overall', 'Band', 'Est. ready', 'Blockers'],
                  readinessReports.map((r) => [
                    r.borrowerName,
                    r.overall,
                    r.band,
                    r.estimatedReadyDate,
                    r.blockers.map((b) => b.title).join('; '),
                  ]),
                )
              }
              className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
            >
              Export readiness
            </button>
          </PortalCard>

          <PortalCard title="Pipeline CSV" description="Active pipeline cards by stage.">
            <button
              type="button"
              onClick={() =>
                exportRowsAsCsv(
                  'lrp-pipeline.csv',
                  ['Borrower', 'Stage', 'Readiness', 'Est. ready', 'LO', 'Days in stage'],
                  pipelineCards.map((c) => [
                    c.borrowerName,
                    STAGE_LABELS[c.stage] ?? c.stage,
                    c.readinessScore,
                    c.estimatedReadyDate,
                    c.loName,
                    c.daysInStage,
                  ]),
                )
              }
              className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
            >
              Export pipeline
            </button>
          </PortalCard>
        </div>
      </div>
    </RoleGate>
  );
}
