'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { documents } from '@/lib/crm/data';

export default function CrmDocumentsPage() {
  return (
    <RoleGate
      permission="documents.view"
      fallback={<p className="text-sm text-slate-500">No access to documents.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Documents"
        description="Partner and borrower artifacts. Platform Documents module is the system of record."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={documents}
          columns={[
            { key: 'name', header: 'Document', cell: (r) => r.name },
            { key: 'category', header: 'Category', cell: (r) => r.category },
            {
              key: 'related',
              header: 'Related',
              cell: (r) => `${r.relatedType}: ${r.relatedName}`,
            },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            { key: 'size', header: 'Size', cell: (r) => r.sizeLabel },
            {
              key: 'at',
              header: 'Uploaded',
              cell: (r) => new Date(r.uploadedAt).toLocaleDateString(),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
