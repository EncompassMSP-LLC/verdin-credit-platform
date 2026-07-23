'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatTile, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { documents, getBorrower, getReadinessForBorrower } from '@/lib/lender/data';
import { STAGE_LABELS } from '@/lib/lender/nav';
import type { LenderDocument } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

const DOC_TONE: Record<string, 'neutral' | 'good' | 'warn' | 'info'> = {
  pending: 'warn',
  in_review: 'info',
  verified: 'good',
  rejected: 'warn',
};

export default function BorrowerDetailPage() {
  const params = useParams<{ id: string }>();
  const borrower = getBorrower(params.id);
  const readiness = getReadinessForBorrower(params.id);
  const borrowerDocs = documents.filter((d) => d.borrowerId === params.id);

  if (!borrower) {
    return (
      <RoleGate permission="borrowers.view">
        <p className="rounded-md border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          Borrower not found.
        </p>
      </RoleGate>
    );
  }

  return (
    <RoleGate permission="borrowers.view">
      <div>
        <PageHeader
          eyebrow="Borrower detail"
          title={borrower.displayName}
          description={`${borrower.email} · ${borrower.phone} · LO ${borrower.loName}. Advisory readiness only—not a funding guarantee.`}
          actions={
            readiness ? (
              <Link
                href="/lender/readiness"
                className="inline-flex rounded-md bg-navy-900 px-3 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
              >
                View readiness report
              </Link>
            ) : null
          }
        />

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatTile
            label="Advisory readiness"
            value={`${borrower.readinessScore || '—'}`}
            hint={borrower.readinessBand}
            tone={borrower.readinessScore >= 80 ? 'good' : 'default'}
          />
          <StatTile
            label="Pipeline stage"
            value={STAGE_LABELS[borrower.stage] ?? borrower.stage}
            hint={`${borrower.progressPct}% milestone progress`}
          />
          <StatTile
            label="Est. ready date"
            value={borrower.estimatedReadyDate ? formatDate(borrower.estimatedReadyDate) : 'TBD'}
            hint="Projected advisory band target"
          />
          <StatTile
            label="Loan target"
            value={
              borrower.loanAmountTarget ? `$${borrower.loanAmountTarget.toLocaleString()}` : '—'
            }
            hint={borrower.propertyState ? `Property state ${borrower.propertyState}` : undefined}
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <PortalCard
            title="Open blockers"
            description="Staff-mediated remediation items from the CRO platform."
          >
            {borrower.blockers.length === 0 ? (
              <p className="text-sm text-slate-500">No open blockers recorded.</p>
            ) : (
              <ul className="space-y-2">
                {borrower.blockers.map((blocker) => (
                  <li
                    key={blocker}
                    className="rounded-md border border-warning/20 bg-warning/5 px-3 py-2 text-sm text-navy-900 dark:text-white"
                  >
                    {blocker}
                  </li>
                ))}
              </ul>
            )}
          </PortalCard>

          <PortalCard
            title="Milestone progress"
            description="Partner-visible checkpoints—not underwriting milestones."
          >
            <ol className="space-y-3">
              {borrower.milestones.map((milestone, index) => (
                <li key={milestone.id} className="flex gap-3">
                  <span
                    className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md text-xs font-bold ${
                      milestone.complete
                        ? 'bg-emerald-600/15 text-emerald-700 dark:text-emerald-400'
                        : 'bg-navy-900/8 text-slate-500 dark:bg-white/10'
                    }`}
                  >
                    {milestone.complete ? '✓' : index + 1}
                  </span>
                  <div>
                    <p className="text-sm font-medium text-navy-900 dark:text-white">
                      {milestone.label}
                    </p>
                    {milestone.completedAt ? (
                      <p className="text-xs text-slate-500">
                        Completed {formatDate(milestone.completedAt)}
                      </p>
                    ) : (
                      <p className="text-xs text-slate-400">Pending</p>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </PortalCard>
        </div>

        <PortalCard
          className="mt-6"
          title="Documents"
          description="Partner-scoped uploads and readiness exports."
        >
          <DataTable<LenderDocument>
            rows={borrowerDocs}
            empty="No documents for this borrower."
            columns={[
              { key: 'name', header: 'Name', cell: (row) => row.name },
              { key: 'category', header: 'Category', cell: (row) => row.category },
              {
                key: 'status',
                header: 'Status',
                cell: (row) => (
                  <StatusPill tone={DOC_TONE[row.status] ?? 'neutral'}>{row.status}</StatusPill>
                ),
              },
              {
                key: 'uploaded',
                header: 'Uploaded',
                cell: (row) => formatDate(row.uploadedAt),
              },
              { key: 'size', header: 'Size', cell: (row) => row.sizeLabel },
            ]}
          />
        </PortalCard>

        {readiness ? (
          <p className="mt-4 text-xs text-slate-500 dark:text-white/50">{readiness.disclaimer}</p>
        ) : null}
      </div>
    </RoleGate>
  );
}
