'use client';

import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { documents as seedDocuments } from '@/lib/lender/data';
import type { DocumentStatus, LenderDocument } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

const DOC_TONE: Record<DocumentStatus, 'neutral' | 'good' | 'warn' | 'info'> = {
  pending: 'warn',
  in_review: 'info',
  verified: 'good',
  rejected: 'warn',
};

export default function DocumentsPage() {
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    if (!query.trim()) return seedDocuments;
    const q = query.toLowerCase();
    return seedDocuments.filter(
      (d) =>
        d.borrowerName.toLowerCase().includes(q) ||
        d.name.toLowerCase().includes(q) ||
        d.category.toLowerCase().includes(q),
    );
  }, [query]);

  return (
    <RoleGate permission="documents.view">
      <div>
        <PageHeader
          eyebrow="Documents"
          title="Partner document library"
          description="Identity, income, dispute evidence, and readiness exports scoped to your borrower cohort."
        />

        <PortalCard
          title="All documents"
          action={
            <input
              type="search"
              placeholder="Search borrower or document…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm dark:border-white/15 dark:bg-navy-900"
            />
          }
        >
          <DataTable<LenderDocument>
            rows={filtered}
            columns={[
              {
                key: 'borrower',
                header: 'Borrower',
                cell: (row) => (
                  <span className="font-medium text-navy-900 dark:text-white">
                    {row.borrowerName}
                  </span>
                ),
              },
              { key: 'name', header: 'Document', cell: (row) => row.name },
              { key: 'category', header: 'Category', cell: (row) => row.category },
              {
                key: 'status',
                header: 'Status',
                cell: (row) => (
                  <StatusPill tone={DOC_TONE[row.status]}>
                    {row.status.replace('_', ' ')}
                  </StatusPill>
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
      </div>
    </RoleGate>
  );
}
