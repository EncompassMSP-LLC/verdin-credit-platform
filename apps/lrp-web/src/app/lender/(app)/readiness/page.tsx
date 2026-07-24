'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { useLenderAuth } from '@/lib/lender/auth';
import { readinessReports } from '@/lib/lender/data';
import { usePartnershipReadinessReports } from '@/lib/lender/readiness-hooks';
import { exportRowsAsCsv } from '@/lib/lender/export';
import type { ReadinessReport } from '@/lib/lender/types';
import type { ReadinessReportSummary } from '@verdin/api-client';
import { formatDate } from '@/lib/utils';

/**
 * Lender readiness page — shows advisory mortgage readiness reports.
 *
 * Disclaimer: Lending Readiness Score™ is an advisory tool for organizing
 * credit and documentation work toward a mortgage conversation. It is not a
 * credit score from a consumer reporting agency, not an underwriting decision,
 * and not a guarantee of loan approval or terms.
 *
 * When the platform API is connected, real reports are fetched via
 * usePartnershipReadinessReports. Demo users fall back to static fixture data.
 */

// Shape shared between the static demo rows and live API rows.
interface DisplayRow {
  id: string;
  borrowerName: string;
  borrowerId: string;
  overall: number;
  band: string;
  generatedAt: string;
  blockerCount: number;
  disclaimer: string;
}

function fromApiSummary(s: ReadinessReportSummary): DisplayRow {
  return {
    id: s.credit_analysis_run_id,
    borrowerName: s.client_display_name ?? '—',
    borrowerId: s.referral_id,
    overall: s.mortgage_readiness_score,
    band: s.band,
    generatedAt: s.generated_at,
    blockerCount: 0, // detail endpoint has blockers; summary omits them
    disclaimer: s.disclaimer,
  };
}

function fromDemoReport(r: ReadinessReport): DisplayRow {
  return {
    id: r.id,
    borrowerName: r.borrowerName,
    borrowerId: r.borrowerId,
    overall: r.overall,
    band: r.band,
    generatedAt: r.generatedAt,
    blockerCount: r.blockers.length,
    disclaimer: r.disclaimer,
  };
}

export default function ReadinessPage() {
  const { can, authMode } = useLenderAuth();

  // Try to pull a partnership ID from localStorage if set by the pipeline/dashboard pages.
  // In demo mode this will be undefined and we fall back to static data.
  const storedPartnershipId =
    typeof window !== 'undefined'
      ? (localStorage.getItem('lrp_active_partnership_id') ?? undefined)
      : undefined;

  const liveQuery = usePartnershipReadinessReports(storedPartnershipId);

  // Rows: prefer live data when available, else use demo fixture.
  const rows: DisplayRow[] =
    authMode === 'platform' && liveQuery.data
      ? liveQuery.data.map(fromApiSummary)
      : readinessReports.map(fromDemoReport);

  const disclaimerText =
    rows[0]?.disclaimer ??
    'Lending Readiness Score™ is an advisory tool for organizing credit and documentation work toward a mortgage conversation. It is not a credit score from a consumer reporting agency, not an underwriting decision, and not a guarantee of loan approval or terms.';

  function exportCsv() {
    exportRowsAsCsv(
      'lrp-readiness-reports.csv',
      ['Borrower', 'Overall', 'Band', 'Generated', 'Blockers'],
      rows.map((r) => [r.borrowerName, r.overall, r.band, r.generatedAt, r.blockerCount]),
    );
  }

  return (
    <RoleGate permission="readiness.view">
      <div>
        <PageHeader
          eyebrow="Readiness reports"
          title="Advisory readiness exports"
          description="Composite readiness for partner and credit review. Not a credit score, underwriting decision, or funding guarantee."
          actions={
            can('readiness.export') ? (
              <button
                type="button"
                onClick={exportCsv}
                className="inline-flex rounded-md bg-navy-900 px-3 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
              >
                Export CSV
              </button>
            ) : null
          }
        />

        {authMode === 'platform' && liveQuery.isLoading && (
          <p className="mb-4 text-sm text-slate-500">Loading readiness reports…</p>
        )}
        {authMode === 'platform' && liveQuery.isError && (
          <p className="mb-4 text-sm text-amber-600 dark:text-amber-400">
            Could not load live readiness reports — showing demo data.
          </p>
        )}

        <PortalCard
          title="Reports"
          description="Generated from borrower remediation progress on the CRO platform."
        >
          <DataTable<DisplayRow>
            rows={rows}
            onRowClick={(row) => {
              window.location.href = `/lender/borrowers/${row.borrowerId}`;
            }}
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
              {
                key: 'overall',
                header: 'Overall',
                cell: (row) => <span className="tabular-nums font-semibold">{row.overall}</span>,
              },
              {
                key: 'band',
                header: 'Band',
                cell: (row) => (
                  <StatusPill tone={row.overall >= 85 ? 'good' : 'info'}>{row.band}</StatusPill>
                ),
              },
              {
                key: 'generated',
                header: 'Generated',
                cell: (row) => formatDate(row.generatedAt),
              },
              {
                key: 'blockers',
                header: 'Blockers',
                cell: (row) => (
                  <span className="text-xs text-slate-500">
                    {row.blockerCount ? `${row.blockerCount} open` : 'None'}
                  </span>
                ),
              },
              {
                key: 'link',
                header: '',
                cell: (row) => (
                  <Link
                    href={`/lender/borrowers/${row.borrowerId}`}
                    className="text-xs font-medium text-gold-700 dark:text-gold-400"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Detail →
                  </Link>
                ),
              },
            ]}
          />
        </PortalCard>

        <p className="mt-4 text-xs text-slate-500 dark:text-white/50">{disclaimerText}</p>
      </div>
    </RoleGate>
  );
}
