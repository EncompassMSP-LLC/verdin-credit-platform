'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { partners } from '@/lib/crm/data';

export default function CrmPartnersPage() {
  return (
    <RoleGate
      permission="partners.view"
      fallback={<p className="text-sm text-slate-500">No access to partners.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Partners"
        description="Lender, realtor, broker, and operator organizations with ownership and referral health."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={partners}
          columns={[
            {
              key: 'name',
              header: 'Partner',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.name}</p>
                  <p className="text-xs text-slate-500">{r.type}</p>
                </div>
              ),
            },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            { key: 'market', header: 'Market', cell: (r) => r.market },
            { key: 'contact', header: 'Primary', cell: (r) => r.primaryContact },
            { key: 'owner', header: 'Owner', cell: (r) => r.ownerName },
            {
              key: 'refs',
              header: 'Active refs',
              cell: (r) => String(r.activeReferrals),
            },
            {
              key: 'funded',
              header: 'Funded YTD',
              cell: (r) => String(r.fundedYtd),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
