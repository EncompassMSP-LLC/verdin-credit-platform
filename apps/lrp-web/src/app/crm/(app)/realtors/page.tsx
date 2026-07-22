'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { realtors } from '@/lib/crm/data';

export default function CrmRealtorsPage() {
  return (
    <RoleGate
      permission="realtors.view"
      fallback={<p className="text-sm text-slate-500">No access to realtors.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Realtors"
        description="Brokerage contacts feeding the readiness pipeline."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={realtors}
          columns={[
            {
              key: 'name',
              header: 'Realtor',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.displayName}</p>
                  <p className="text-xs text-slate-500">{r.email}</p>
                </div>
              ),
            },
            { key: 'brokerage', header: 'Brokerage', cell: (r) => r.brokerage },
            { key: 'market', header: 'Market', cell: (r) => r.market },
            {
              key: 'lender',
              header: 'Preferred lender',
              cell: (r) => r.preferredLender ?? '—',
            },
            {
              key: 'borrowers',
              header: 'Active borrowers',
              cell: (r) => String(r.activeBorrowers),
            },
            {
              key: 'refs',
              header: 'Open referrals',
              cell: (r) => String(r.openReferrals),
            },
            { key: 'status', header: 'Status', cell: (r) => r.status },
          ]}
        />
      </div>
    </RoleGate>
  );
}
