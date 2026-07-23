'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable, type Column } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { useLenderAuth } from '@/lib/lender/auth';
import { pipelineCards } from '@/lib/lender/data';
import {
  pickPrimaryPartnership,
  useLenderPartnerships,
  useLenderReferrals,
  useMortgagePartnerStatus,
  type PartnerReferral,
} from '@/lib/lender/partner-hooks';
import { formatDate } from '@/lib/utils';

const STATUS_LABELS: Record<string, string> = {
  new: 'New',
  accepted: 'Accepted',
  in_progress: 'In progress',
  completed: 'Completed',
  declined: 'Declined',
};

type PipelineRow = {
  id: string;
  borrower: string;
  status: string;
  source: string;
  updatedAt: string;
  href?: string;
};

function referralToRow(row: PartnerReferral): PipelineRow {
  return {
    id: row.id,
    borrower: row.client_display_name?.trim() || `Client ${row.client_id.slice(0, 8)}`,
    status: STATUS_LABELS[row.status] ?? row.status,
    source: row.source_label?.trim() || '—',
    updatedAt: row.updated_at,
    href: `/lender/borrowers/${row.client_id}`,
  };
}

function demoRows(): PipelineRow[] {
  return pipelineCards.map((card) => ({
    id: card.id,
    borrower: card.borrowerName,
    status: card.stage.replace(/_/g, ' '),
    source: card.loName,
    updatedAt: card.estimatedReadyDate ?? new Date().toISOString(),
    href: `/lender/borrowers/${card.borrowerId}`,
  }));
}

const columns: Column<PipelineRow>[] = [
  {
    key: 'borrower',
    header: 'Borrower',
    cell: (row) => <span className="font-medium text-navy-900">{row.borrower}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    cell: (row) => <StatusPill tone="info">{row.status}</StatusPill>,
  },
  {
    key: 'band',
    header: 'Readiness band',
    cell: () => <span className="text-slate-400">—</span>,
  },
  {
    key: 'source',
    header: 'Source',
    cell: (row) => row.source,
  },
  {
    key: 'updated',
    header: 'Updated',
    cell: (row) => formatDate(row.updatedAt),
  },
];

/**
 * Spec: Vol 20 · pages/pipeline.md (table-first; kanban deferred)
 * Platform auth → mortgage_partner referrals; demo → seed rows.
 */
export default function PipelinePage() {
  const router = useRouter();
  const { authMode } = useLenderAuth();
  const statusQuery = useMortgagePartnerStatus();
  const partnershipsQuery = useLenderPartnerships();
  const partnership = pickPrimaryPartnership(partnershipsQuery.data);
  const referralsQuery = useLenderReferrals(partnership?.id);

  const isDemo = authMode === 'demo';
  const platformEnabled = statusQuery.data?.mortgage_partner_enabled === true;

  let rows: PipelineRow[] = [];
  let loading = false;
  let errorMessage: string | null = null;

  if (isDemo) {
    rows = demoRows();
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
    rows = (referralsQuery.data ?? []).map(referralToRow);
  }

  return (
    <RoleGate permission="pipeline.view">
      <div>
        <PageHeader
          eyebrow="Pipeline"
          title="Referral pipeline"
          description={`${ADVISORY_DISCLAIMER_SHORT} Referral status is operational tracking—not underwriting.`}
          actions={
            <Link
              href="/lender/referrals"
              className="inline-flex rounded-brand border border-lrp-border bg-lrp-surface-elevated px-4 py-2.5 text-sm font-semibold text-navy-900 hover:bg-lrp-surface"
            >
              All referrals
            </Link>
          }
        />

        {isDemo ? (
          <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
            Demo mode — showing sample pipeline rows. Sign in with a platform staff account to load
            live partnership referrals.
          </p>
        ) : null}

        {partnership && !isDemo ? (
          <p className="mb-4 text-sm text-slate-600">
            Partnership:{' '}
            <span className="font-medium text-navy-900">{partnership.display_name}</span>
          </p>
        ) : null}

        <PortalCard
          title="Open referrals"
          description="Table view of partnership referrals (Vol 20). Readiness band and next-update columns land when score publish is linked."
        >
          {loading ? (
            <p className="text-sm text-slate-500">Loading referrals…</p>
          ) : errorMessage ? (
            <p className="rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
              {errorMessage}
            </p>
          ) : (
            <DataTable
              columns={columns}
              rows={rows}
              empty="No referrals in this partnership yet."
              onRowClick={(row) => {
                if (row.href) {
                  router.push(row.href);
                }
              }}
            />
          )}
        </PortalCard>
      </div>
    </RoleGate>
  );
}
