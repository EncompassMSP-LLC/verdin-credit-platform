'use client';

import Link from 'next/link';
import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { borrowers } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';

export default function CrmBorrowersPage() {
  return (
    <RoleGate
      permission="borrowers.view"
      fallback={<p className="text-sm text-slate-500">No access to borrowers.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Borrowers"
        description="Maps to platform Clients + Cases. Readiness scores are advisory for partner handoff."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={borrowers}
          columns={[
            {
              key: 'name',
              header: 'Borrower',
              cell: (r) => (
                <Link
                  href={`/crm/borrowers/${r.id}`}
                  className="font-medium text-gold-700 hover:underline dark:text-gold-400"
                >
                  {r.displayName}
                </Link>
              ),
            },
            {
              key: 'stage',
              header: 'Stage',
              cell: (r) => STAGE_LABELS[r.stage] ?? r.stage,
            },
            {
              key: 'score',
              header: 'Score',
              cell: (r) => `${r.readinessScore} · ${r.readinessBand}`,
            },
            { key: 'lo', header: 'LO', cell: (r) => r.loName },
            {
              key: 'lender',
              header: 'Lender',
              cell: (r) => r.lenderName ?? '—',
            },
            {
              key: 'realtor',
              header: 'Realtor',
              cell: (r) => r.realtorName ?? '—',
            },
            {
              key: 'progress',
              header: 'Progress',
              cell: (r) => `${r.progressPct}%`,
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
