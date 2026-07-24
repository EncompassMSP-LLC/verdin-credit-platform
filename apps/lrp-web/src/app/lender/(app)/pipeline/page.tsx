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
import { STAGE_LABELS } from '@/lib/lender/nav';
import {
  pickPrimaryPartnership,
  useLenderPartnerships,
  useLenderPipeline,
  useMortgagePartnerStatus,
  type PipelineCard,
} from '@/lib/lender/partner-hooks';
import { formatDate } from '@/lib/utils';

type PipelineRow = {
  id: string;
  borrower: string;
  stage: string;
  stageRaw: string;
  daysInStage: number;
  source: string;
  changedAt: string | null;
  href?: string;
};

function apiCardToRow(card: PipelineCard): PipelineRow {
  return {
    id: card.referral_id,
    borrower: card.client_display_name?.trim() || `Client ${card.client_id.slice(0, 8)}`,
    stage: STAGE_LABELS[card.pipeline_stage] ?? card.pipeline_stage.replace(/_/g, ' '),
    stageRaw: card.pipeline_stage,
    daysInStage: card.days_in_stage,
    source: card.source_label?.trim() || '—',
    changedAt: card.stage_changed_at,
    href: `/lender/borrowers/${card.client_id}`,
  };
}

function demoRows(): PipelineRow[] {
  return pipelineCards.map((card) => ({
    id: card.id,
    borrower: card.borrowerName,
    stage: STAGE_LABELS[card.stage] ?? card.stage.replace(/_/g, ' '),
    stageRaw: card.stage,
    daysInStage: 0,
    source: card.loName,
    changedAt: card.estimatedReadyDate ?? null,
    href: `/lender/borrowers/${card.borrowerId}`,
  }));
}

function stageTone(stage: string): 'good' | 'info' | 'warn' | 'neutral' | undefined {
  if (stage === 'mortgage_ready' || stage === 'funded') return 'good';
  if (stage === 'declined' || stage === 'withdrawn') return 'warn';
  return 'info';
}

const columns: Column<PipelineRow>[] = [
  {
    key: 'borrower',
    header: 'Borrower',
    cell: (row) => (
      <span className="font-medium text-navy-900 dark:text-white">{row.borrower}</span>
    ),
  },
  {
    key: 'stage',
    header: 'Pipeline stage',
    cell: (row) => <StatusPill tone={stageTone(row.stageRaw)}>{row.stage}</StatusPill>,
  },
  {
    key: 'daysInStage',
    header: 'Days in stage',
    cell: (row) => (
      <span className="tabular-nums text-slate-700 dark:text-slate-300">{row.daysInStage}</span>
    ),
  },
  {
    key: 'source',
    header: 'Source',
    cell: (row) => row.source,
  },
  {
    key: 'changedAt',
    header: 'Stage updated',
    cell: (row) => (row.changedAt ? formatDate(row.changedAt) : '—'),
  },
];

/**
 * Spec: Vol 20 · pages/pipeline.md (table-first; kanban deferred)
 * Platform auth → /partnerships/{id}/pipeline cards; demo → seed rows.
 */
export default function PipelinePage() {
  const router = useRouter();
  const { authMode } = useLenderAuth();
  const statusQuery = useMortgagePartnerStatus();
  const partnershipsQuery = useLenderPartnerships();
  const partnership = pickPrimaryPartnership(partnershipsQuery.data);
  const pipelineQuery = useLenderPipeline(partnership?.id);

  const isDemo = authMode === 'demo';
  const platformEnabled = statusQuery.data?.mortgage_partner_enabled === true;

  let rows: PipelineRow[] = [];
  let loading = false;
  let errorMessage: string | null = null;

  if (isDemo) {
    rows = demoRows();
  } else if (statusQuery.isLoading || partnershipsQuery.isLoading || pipelineQuery.isLoading) {
    loading = true;
  } else if (statusQuery.isError || partnershipsQuery.isError || pipelineQuery.isError) {
    errorMessage =
      'Could not load partnership pipeline. Confirm the API is running and ENABLE_MORTGAGE_PARTNER=true.';
  } else if (!platformEnabled) {
    errorMessage = 'Mortgage Partner edition is not enabled on this API.';
  } else if (!partnership) {
    errorMessage = 'No partnerships found for this organization yet.';
  } else {
    rows = (pipelineQuery.data ?? []).map(apiCardToRow);
  }

  return (
    <RoleGate permission="pipeline.view">
      <div>
        <PageHeader
          eyebrow="Pipeline"
          title="Referral pipeline"
          description={`${ADVISORY_DISCLAIMER_SHORT} Referral stage is operational tracking—not underwriting.`}
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
            live partnership pipeline.
          </p>
        ) : null}

        {partnership && !isDemo ? (
          <p className="mb-4 text-sm text-slate-600">
            Partnership:{' '}
            <span className="font-medium text-navy-900">{partnership.display_name}</span>
          </p>
        ) : null}

        <PortalCard
          title="Pipeline board"
          description="Ordered by most-recent stage change. Stage updates reflect CRO-mediated progress — advisory tracking only."
        >
          {loading ? (
            <p className="text-sm text-slate-500">Loading pipeline…</p>
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
