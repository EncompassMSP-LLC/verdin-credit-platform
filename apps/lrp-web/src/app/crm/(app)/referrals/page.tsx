'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { referrals } from '@/lib/crm/data';

export default function CrmReferralsPage() {
  return (
    <RoleGate
      permission="referrals.view"
      fallback={<p className="text-sm text-slate-500">No access to referrals.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Referral tracking"
        description="Attribution from lender, realtor, partner, and web sources through accept → convert."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={referrals}
          columns={[
            {
              key: 'borrower',
              header: 'Borrower',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.borrowerName}</p>
                  <p className="text-xs text-slate-500">{r.borrowerEmail}</p>
                </div>
              ),
            },
            {
              key: 'source',
              header: 'Source',
              cell: (r) => (
                <div>
                  <p className="font-medium capitalize">{r.sourceType}</p>
                  <p className="text-xs text-slate-500">{r.sourceName}</p>
                </div>
              ),
            },
            { key: 'lo', header: 'LO', cell: (r) => r.loName },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            {
              key: 'at',
              header: 'Referred',
              cell: (r) => new Date(r.referredAt).toLocaleDateString(),
            },
            {
              key: 'value',
              header: 'Loan goal $',
              cell: (r) =>
                r.conversionValue != null
                  ? r.conversionValue.toLocaleString('en-US', {
                      style: 'currency',
                      currency: 'USD',
                      maximumFractionDigits: 0,
                    })
                  : '—',
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
