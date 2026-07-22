'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { emailMessages } from '@/lib/crm/data';

export default function CrmEmailPage() {
  return (
    <RoleGate
      permission="email.view"
      fallback={<p className="text-sm text-slate-500">No access to email.</p>}
    >
      <PageHeader
        eyebrow="Engagement"
        title="Email"
        description="Partner digests and borrower notices via notifications email delivery audit."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={emailMessages}
          columns={[
            {
              key: 'to',
              header: 'To',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.toName}</p>
                  <p className="text-xs text-slate-500">{r.toEmail}</p>
                </div>
              ),
            },
            { key: 'subject', header: 'Subject', cell: (r) => r.subject },
            { key: 'preview', header: 'Preview', cell: (r) => r.preview },
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
