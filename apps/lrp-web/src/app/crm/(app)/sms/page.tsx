'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { smsMessages } from '@/lib/crm/data';

export default function CrmSmsPage() {
  return (
    <RoleGate
      permission="sms.view"
      fallback={<p className="text-sm text-slate-500">No access to SMS.</p>}
    >
      <PageHeader
        eyebrow="Engagement"
        title="SMS"
        description="Outbound/inbound SMS ledger wired to notifications SMS delivery on the platform API."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={smsMessages}
          columns={[
            {
              key: 'to',
              header: 'Contact',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.toName}</p>
                  <p className="text-xs text-slate-500">{r.toPhone}</p>
                </div>
              ),
            },
            { key: 'dir', header: 'Dir', cell: (r) => r.direction },
            { key: 'body', header: 'Message', cell: (r) => r.body },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            {
              key: 'at',
              header: 'When',
              cell: (r) => new Date(r.sentAt).toLocaleString(),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
