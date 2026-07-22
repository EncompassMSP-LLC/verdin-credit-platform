'use client';

import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { referrals as seedReferrals } from '@/lib/lender/data';
import type { Referral, ReferralStatus } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

const STATUS_TONE: Record<ReferralStatus, 'neutral' | 'good' | 'warn' | 'info'> = {
  new: 'info',
  accepted: 'good',
  in_progress: 'info',
  completed: 'good',
  declined: 'warn',
};

const STATUS_LABEL: Record<ReferralStatus, string> = {
  new: 'New',
  accepted: 'Accepted',
  in_progress: 'In progress',
  completed: 'Completed',
  declined: 'Declined',
};

export default function ReferralsPage() {
  const [rows, setRows] = useState<Referral[]>(seedReferrals);
  const [statusFilter, setStatusFilter] = useState<ReferralStatus | 'all'>('all');
  const [query, setQuery] = useState('');

  const filtered = useMemo(() => {
    return rows.filter((row) => {
      if (statusFilter !== 'all' && row.status !== statusFilter) return false;
      if (!query.trim()) return true;
      const q = query.toLowerCase();
      return (
        row.borrowerName.toLowerCase().includes(q) ||
        row.borrowerEmail.toLowerCase().includes(q) ||
        row.source.toLowerCase().includes(q) ||
        row.targetProduct.toLowerCase().includes(q)
      );
    });
  }, [rows, statusFilter, query]);

  function updateStatus(id: string, status: ReferralStatus) {
    setRows((prev) => prev.map((r) => (r.id === id ? { ...r, status } : r)));
  }

  return (
    <RoleGate permission="referrals.manage">
      <div>
        <PageHeader
          eyebrow="Referral management"
          title="Partner referrals"
          description="Accept or decline new referrals and track intake progress. Status changes are local demo state until Mortgage Partner APIs ship."
        />

        <PortalCard
          title="Referral queue"
          description="Filter by status or search borrower, source, or product."
          action={
            <div className="flex flex-wrap items-center gap-2">
              <input
                type="search"
                placeholder="Search referrals…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm dark:border-white/15 dark:bg-navy-900"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as ReferralStatus | 'all')}
                className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm dark:border-white/15 dark:bg-navy-900"
              >
                <option value="all">All statuses</option>
                {(Object.keys(STATUS_LABEL) as ReferralStatus[]).map((status) => (
                  <option key={status} value={status}>
                    {STATUS_LABEL[status]}
                  </option>
                ))}
              </select>
            </div>
          }
        >
          <DataTable<Referral>
            rows={filtered}
            empty="No referrals match your filters."
            columns={[
              {
                key: 'borrower',
                header: 'Borrower',
                cell: (row) => (
                  <div>
                    <p className="font-medium text-navy-900 dark:text-white">{row.borrowerName}</p>
                    <p className="text-xs text-slate-500">{row.borrowerEmail}</p>
                  </div>
                ),
              },
              {
                key: 'source',
                header: 'Source',
                cell: (row) => row.source,
              },
              {
                key: 'product',
                header: 'Product',
                cell: (row) => row.targetProduct,
              },
              {
                key: 'lo',
                header: 'LO',
                cell: (row) => row.loName,
              },
              {
                key: 'referred',
                header: 'Referred',
                cell: (row) => formatDate(row.referredAt),
              },
              {
                key: 'status',
                header: 'Status',
                cell: (row) => (
                  <StatusPill tone={STATUS_TONE[row.status]}>{STATUS_LABEL[row.status]}</StatusPill>
                ),
              },
              {
                key: 'actions',
                header: 'Actions',
                cell: (row) =>
                  row.status === 'new' ? (
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        onClick={() => updateStatus(row.id, 'accepted')}
                        className="rounded-md bg-navy-900 px-2.5 py-1 text-xs font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
                      >
                        Accept
                      </button>
                      <button
                        type="button"
                        onClick={() => updateStatus(row.id, 'declined')}
                        className="rounded-md border border-critical/30 px-2.5 py-1 text-xs font-semibold text-critical hover:bg-critical/10"
                      >
                        Decline
                      </button>
                    </div>
                  ) : (
                    <span className="text-xs text-slate-400">—</span>
                  ),
              },
            ]}
          />
        </PortalCard>
      </div>
    </RoleGate>
  );
}
