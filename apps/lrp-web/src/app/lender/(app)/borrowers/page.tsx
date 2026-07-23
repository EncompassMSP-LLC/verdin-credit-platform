'use client';

import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { borrowers } from '@/lib/lender/data';
import { STAGE_LABELS } from '@/lib/lender/nav';
import type { Borrower } from '@/lib/lender/types';
import { formatDate, formatPercent } from '@/lib/utils';

export default function BorrowersPage() {
  const router = useRouter();

  return (
    <RoleGate permission="borrowers.view">
      <div>
        <PageHeader
          eyebrow="Borrower tracking"
          title="Active borrower cohort"
          description="Track remediation progress and advisory readiness bands. Scores support partner handoff—not loan approval guarantees."
        />

        <PortalCard title="Borrowers" description="Click a row to open borrower detail.">
          <DataTable<Borrower>
            rows={borrowers}
            onRowClick={(row) => router.push(`/lender/borrowers/${row.id}`)}
            columns={[
              {
                key: 'name',
                header: 'Borrower',
                cell: (row) => (
                  <div>
                    <p className="font-medium text-navy-900 dark:text-white">{row.displayName}</p>
                    <p className="text-xs text-slate-500">{row.email}</p>
                  </div>
                ),
              },
              {
                key: 'lo',
                header: 'Loan officer',
                cell: (row) => row.loName,
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
                key: 'readiness',
                header: 'Readiness',
                cell: (row) => (
                  <div>
                    <span className="tabular-nums font-medium">{row.readinessScore || '—'}</span>
                    <p className="text-xs text-slate-500">{row.readinessBand}</p>
                  </div>
                ),
              },
              {
                key: 'ready',
                header: 'Est. ready',
                cell: (row) => (row.estimatedReadyDate ? formatDate(row.estimatedReadyDate) : '—'),
              },
              {
                key: 'progress',
                header: 'Progress',
                cell: (row) => (
                  <div className="min-w-[7rem]">
                    <div className="flex items-center justify-between text-xs">
                      <span className="tabular-nums">{formatPercent(row.progressPct)}</span>
                    </div>
                    <div className="mt-1 h-1.5 overflow-hidden rounded-md bg-navy-900/10 dark:bg-white/10">
                      <div
                        className="h-full rounded-md bg-gold-500"
                        style={{ width: `${row.progressPct}%` }}
                      />
                    </div>
                  </div>
                ),
              },
              {
                key: 'activity',
                header: 'Last activity',
                cell: (row) => formatDate(row.lastActivityAt),
              },
            ]}
          />
        </PortalCard>
      </div>
    </RoleGate>
  );
}
