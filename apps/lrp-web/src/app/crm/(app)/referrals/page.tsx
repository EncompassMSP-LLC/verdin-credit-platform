'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { useCrmAuth } from '@/lib/crm/auth';
import { referrals as seedReferrals } from '@/lib/crm/data';
import {
  pickPrimaryPartnership,
  useCrmMortgagePartnerStatus,
  useCrmPartnerships,
  useCrmReferrals,
  useUpdateCrmReferral,
  type PartnerReferral,
  type PartnerReferralStatus,
} from '@/lib/crm/partner-hooks';
import { formatDate } from '@/lib/utils';

type StatusTab = 'all' | 'new' | 'accepted' | 'declined';

type ReferralRow = {
  id: string;
  borrowerName: string;
  partner: string;
  status: PartnerReferralStatus | string;
  referredAt: string;
  clientId?: string;
};

const TABS: { id: StatusTab; label: string }[] = [
  { id: 'new', label: 'New' },
  { id: 'accepted', label: 'Accepted' },
  { id: 'declined', label: 'Declined' },
  { id: 'all', label: 'All' },
];

function platformRow(row: PartnerReferral, partnerName: string): ReferralRow {
  return {
    id: row.id,
    borrowerName: row.client_display_name?.trim() || `Client ${row.client_id.slice(0, 8)}`,
    partner: partnerName,
    status: row.status,
    referredAt: row.created_at,
    clientId: row.client_id,
  };
}

/**
 * Spec: Vol 21 · pages/referrals.md
 * Platform auth → mortgage_partner referrals + PATCH; demo → seed rows.
 */
export default function CrmReferralsPage() {
  const router = useRouter();
  const { authMode, can } = useCrmAuth();
  const statusQuery = useCrmMortgagePartnerStatus();
  const partnershipsQuery = useCrmPartnerships();
  const partnership = pickPrimaryPartnership(partnershipsQuery.data);
  const referralsQuery = useCrmReferrals(partnership?.id);
  const updateReferral = useUpdateCrmReferral(partnership?.id);

  const isDemo = authMode === 'demo';
  const platformEnabled = statusQuery.data?.mortgage_partner_enabled === true;
  const canManage = can('referrals.manage');

  const [tab, setTab] = useState<StatusTab>('new');
  const [actionError, setActionError] = useState<string | null>(null);
  const [demoOverrides, setDemoOverrides] = useState<Record<string, string>>({});

  const loading =
    !isDemo && (statusQuery.isLoading || partnershipsQuery.isLoading || referralsQuery.isLoading);

  const errorMessage = useMemo(() => {
    if (isDemo || loading) return null;
    if (statusQuery.isError || partnershipsQuery.isError || referralsQuery.isError) {
      return 'Could not load partnership referrals. Confirm the API is running and ENABLE_MORTGAGE_PARTNER=true.';
    }
    if (!platformEnabled) return 'Mortgage Partner edition is not enabled on this API.';
    if (!partnership) return 'No partnerships found for this organization yet.';
    return null;
  }, [
    isDemo,
    loading,
    statusQuery.isError,
    partnershipsQuery.isError,
    referralsQuery.isError,
    platformEnabled,
    partnership,
  ]);

  const rows = useMemo((): ReferralRow[] => {
    if (isDemo) {
      return seedReferrals.map((r) => ({
        id: r.id,
        borrowerName: r.borrowerName,
        partner: r.sourceName,
        status: demoOverrides[r.id] ?? r.status,
        referredAt: r.referredAt,
      }));
    }
    if (errorMessage || !partnership) return [];
    const partnerName = partnership.display_name;
    return (referralsQuery.data ?? []).map((row) => platformRow(row, partnerName));
  }, [isDemo, demoOverrides, errorMessage, partnership, referralsQuery.data]);

  const filtered = useMemo(() => {
    if (tab === 'all') return rows;
    return rows.filter((row) => row.status === tab);
  }, [rows, tab]);

  async function updateStatus(row: ReferralRow, status: 'accepted' | 'declined') {
    setActionError(null);
    if (isDemo) {
      setDemoOverrides((prev) => ({ ...prev, [row.id]: status }));
      return;
    }
    try {
      await updateReferral.mutateAsync({ referralId: row.id, status });
      if (status === 'accepted' && row.clientId) {
        router.push(`/crm/borrowers/${row.clientId}`);
      }
    } catch {
      setActionError('Could not update referral status. Admin write access is required.');
    }
  }

  return (
    <RoleGate
      permission="referrals.view"
      fallback={<p className="text-sm text-slate-500">No access to referrals.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Referral queue"
        description={`${ADVISORY_DISCLAIMER_SHORT} Accept does not mean loan approval—triage into borrower workspace only.`}
      />

      {isDemo ? (
        <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
          Demo mode — showing sample referrals. Sign in with a platform staff account to load live
          partnership referrals.
        </p>
      ) : null}

      {partnership && !isDemo ? (
        <p className="mb-4 text-sm text-slate-600">
          Partnership: <span className="font-medium text-navy-900">{partnership.display_name}</span>
        </p>
      ) : null}

      {actionError ? (
        <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          {actionError}
        </p>
      ) : null}

      <div className="mb-4 flex flex-wrap gap-2">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setTab(item.id)}
            className={
              tab === item.id
                ? 'rounded-md bg-navy-900 px-3 py-1.5 text-sm font-semibold text-white'
                : 'rounded-md border border-navy-900/15 bg-white px-3 py-1.5 text-sm text-navy-900 hover:bg-lrp-surface'
            }
          >
            {item.label}
          </button>
        ))}
      </div>

      <div className="rounded-md border border-navy-900/10 bg-white">
        {loading ? (
          <p className="p-4 text-sm text-slate-500">Loading referrals…</p>
        ) : errorMessage ? (
          <p className="m-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
            {errorMessage}
          </p>
        ) : (
          <DataTable
            rows={filtered}
            empty="No referrals in this tab."
            columns={[
              {
                key: 'borrower',
                header: 'Borrower',
                cell: (r) =>
                  r.clientId ? (
                    <Link
                      href={`/crm/borrowers/${r.clientId}`}
                      className="font-medium text-gold-700 hover:underline"
                    >
                      {r.borrowerName}
                    </Link>
                  ) : (
                    <span className="font-medium text-navy-900">{r.borrowerName}</span>
                  ),
              },
              {
                key: 'partner',
                header: 'Partner',
                cell: (r) => r.partner,
              },
              {
                key: 'status',
                header: 'Status',
                cell: (r) => (
                  <span className="capitalize">{String(r.status).replace(/_/g, ' ')}</span>
                ),
              },
              {
                key: 'at',
                header: 'Referred',
                cell: (r) => formatDate(r.referredAt),
              },
              {
                key: 'actions',
                header: 'Actions',
                cell: (r) =>
                  canManage && r.status === 'new' ? (
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        disabled={updateReferral.isPending}
                        onClick={() => void updateStatus(r, 'accepted')}
                        className="rounded-md bg-navy-900 px-2.5 py-1 text-xs font-semibold text-white hover:bg-navy-700 disabled:opacity-50"
                      >
                        Accept
                      </button>
                      <button
                        type="button"
                        disabled={updateReferral.isPending}
                        onClick={() => void updateStatus(r, 'declined')}
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
      </div>
    </RoleGate>
  );
}
