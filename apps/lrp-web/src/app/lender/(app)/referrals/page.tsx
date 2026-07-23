'use client';

import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { useLenderAuth } from '@/lib/lender/auth';
import { referrals as seedReferrals } from '@/lib/lender/data';
import {
  pickPrimaryPartnership,
  useLenderPartnerships,
  useLenderReferrals,
  useMortgagePartnerStatus,
  useUpdateLenderReferral,
  type PartnerReferral,
  type PartnerReferralStatus,
} from '@/lib/lender/partner-hooks';
import type { Referral, ReferralStatus } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

const STATUS_TONE: Record<PartnerReferralStatus, 'neutral' | 'good' | 'warn' | 'info'> = {
  new: 'info',
  accepted: 'good',
  in_progress: 'info',
  completed: 'good',
  declined: 'warn',
};

const STATUS_LABEL: Record<PartnerReferralStatus, string> = {
  new: 'New',
  accepted: 'Accepted',
  in_progress: 'In progress',
  completed: 'Completed',
  declined: 'Declined',
};

type ReferralRow = {
  id: string;
  borrowerName: string;
  borrowerEmail: string;
  source: string;
  targetProduct: string;
  loName: string;
  referredAt: string;
  status: PartnerReferralStatus;
  href?: string;
};

function platformRow(row: PartnerReferral): ReferralRow {
  return {
    id: row.id,
    borrowerName: row.client_display_name?.trim() || `Client ${row.client_id.slice(0, 8)}`,
    borrowerEmail: '',
    source: row.source_label?.trim() || '—',
    targetProduct: '—',
    loName: '—',
    referredAt: row.created_at,
    status: row.status,
    href: `/lender/borrowers/${row.client_id}`,
  };
}

function seedRow(row: Referral): ReferralRow {
  return {
    id: row.id,
    borrowerName: row.borrowerName,
    borrowerEmail: row.borrowerEmail,
    source: row.source,
    targetProduct: row.targetProduct,
    loName: row.loName,
    referredAt: row.referredAt,
    status: row.status,
    href: `/lender/borrowers/${row.borrowerId}`,
  };
}

/**
 * Spec: Vol 20 · pages/referral-management.md
 * Platform auth → mortgage_partner referrals + PATCH status; demo → seed rows.
 */
export default function ReferralsPage() {
  const { authMode } = useLenderAuth();
  const statusQuery = useMortgagePartnerStatus();
  const partnershipsQuery = useLenderPartnerships();
  const partnership = pickPrimaryPartnership(partnershipsQuery.data);
  const referralsQuery = useLenderReferrals(partnership?.id);
  const updateReferral = useUpdateLenderReferral(partnership?.id);

  const isDemo = authMode === 'demo';
  const platformEnabled = statusQuery.data?.mortgage_partner_enabled === true;

  const [demoRows, setDemoRows] = useState<Referral[]>(seedReferrals);
  const [statusFilter, setStatusFilter] = useState<PartnerReferralStatus | 'all'>('all');
  const [query, setQuery] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  let rows: ReferralRow[] = [];
  let loading = false;
  let errorMessage: string | null = null;

  if (isDemo) {
    rows = demoRows.map(seedRow);
  } else if (statusQuery.isLoading || partnershipsQuery.isLoading || referralsQuery.isLoading) {
    loading = true;
  } else if (statusQuery.isError || partnershipsQuery.isError || referralsQuery.isError) {
    errorMessage =
      'Could not load partnership referrals. Confirm the API is running and ENABLE_MORTGAGE_PARTNER=true.';
  } else if (!platformEnabled) {
    errorMessage = 'Mortgage Partner edition is not enabled on this API.';
  } else if (!partnership) {
    errorMessage = 'No partnerships found for this organization yet.';
  } else {
    rows = (referralsQuery.data ?? []).map(platformRow);
  }

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

  async function updateStatus(id: string, status: PartnerReferralStatus) {
    setActionError(null);
    if (isDemo) {
      setDemoRows((prev) =>
        prev.map((r) => (r.id === id ? { ...r, status: status as ReferralStatus } : r)),
      );
      return;
    }
    try {
      await updateReferral.mutateAsync({ referralId: id, status });
    } catch {
      setActionError('Could not update referral status. Admin write access is required.');
    }
  }

  return (
    <RoleGate permission="referrals.manage">
      <div>
        <PageHeader
          eyebrow="Referral management"
          title="Partner referrals"
          description={`${ADVISORY_DISCLAIMER_SHORT} Accept or decline new referrals and track intake progress—not underwriting.`}
        />

        {isDemo ? (
          <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
            Demo mode — showing sample referrals. Sign in with a platform staff account to load live
            partnership referrals.
          </p>
        ) : null}

        {partnership && !isDemo ? (
          <p className="mb-4 text-sm text-slate-600">
            Partnership:{' '}
            <span className="font-medium text-navy-900">{partnership.display_name}</span>
          </p>
        ) : null}

        {actionError ? (
          <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
            {actionError}
          </p>
        ) : null}

        <PortalCard
          title="Referral queue"
          description="Filter by status or search borrower or source. Status changes are audited."
          action={
            <div className="flex flex-wrap items-center gap-2">
              <input
                type="search"
                placeholder="Search referrals…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm"
              />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as PartnerReferralStatus | 'all')}
                className="rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm"
              >
                <option value="all">All statuses</option>
                {(Object.keys(STATUS_LABEL) as PartnerReferralStatus[]).map((status) => (
                  <option key={status} value={status}>
                    {STATUS_LABEL[status]}
                  </option>
                ))}
              </select>
            </div>
          }
        >
          {loading ? (
            <p className="text-sm text-slate-500">Loading referrals…</p>
          ) : errorMessage ? (
            <p className="rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
              {errorMessage}
            </p>
          ) : (
            <DataTable<ReferralRow>
              rows={filtered}
              empty="No referrals match your filters."
              columns={[
                {
                  key: 'borrower',
                  header: 'Borrower',
                  cell: (row) => (
                    <div>
                      <p className="font-medium text-navy-900">{row.borrowerName}</p>
                      {row.borrowerEmail ? (
                        <p className="text-xs text-slate-500">{row.borrowerEmail}</p>
                      ) : null}
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
                    <StatusPill tone={STATUS_TONE[row.status]}>
                      {STATUS_LABEL[row.status]}
                    </StatusPill>
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
                          disabled={updateReferral.isPending}
                          onClick={() => void updateStatus(row.id, 'accepted')}
                          className="rounded-md bg-navy-900 px-2.5 py-1 text-xs font-semibold text-white hover:bg-navy-700 disabled:opacity-50"
                        >
                          Accept
                        </button>
                        <button
                          type="button"
                          disabled={updateReferral.isPending}
                          onClick={() => void updateStatus(row.id, 'declined')}
                          className="rounded-md border border-critical/30 px-2.5 py-1 text-xs font-semibold text-critical hover:bg-critical/10 disabled:opacity-50"
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
          )}
        </PortalCard>
      </div>
    </RoleGate>
  );
}
