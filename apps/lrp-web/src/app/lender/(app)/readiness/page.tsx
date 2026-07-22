'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { DataTable } from '@/components/lender/DataTable';
import { RoleGate } from '@/components/lender/RoleGate';
import { useLenderAuth } from '@/lib/lender/auth';
import { readinessReports } from '@/lib/lender/data';
import { exportRowsAsCsv } from '@/lib/lender/export';
import type { ReadinessReport } from '@/lib/lender/types';
import { formatDate } from '@/lib/utils';

export default function ReadinessPage() {
  const { can } = useLenderAuth();

  function exportCsv() {
    exportRowsAsCsv(
      'lrp-readiness-reports.csv',
      ['Borrower', 'Overall', 'Band', 'Est. ready', 'Generated', 'Blockers'],
      readinessReports.map((r) => [
        r.borrowerName,
        r.overall,
        r.band,
        r.estimatedReadyDate,
        r.generatedAt,
        r.blockers.map((b) => b.title).join('; '),
      ]),
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

        <PortalCard
          title="Reports"
          description="Generated from borrower remediation progress on the CRO platform."
        >
          <DataTable<ReadinessReport>
            rows={readinessReports}
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
                key: 'ready',
                header: 'Est. ready',
                cell: (row) => (row.estimatedReadyDate ? formatDate(row.estimatedReadyDate) : '—'),
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
                    {row.blockers.length ? `${row.blockers.length} open` : 'None'}
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

        <p className="mt-4 text-xs text-slate-500 dark:text-white/50">
          {readinessReports[0]?.disclaimer ??
            'Advisory readiness composite for partner handoff—not a credit score, underwriting decision, or funding guarantee.'}
        </p>
      </div>
    </RoleGate>
  );
}
