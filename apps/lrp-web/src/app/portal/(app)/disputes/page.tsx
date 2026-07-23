'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePortalCaseDetail, usePrimaryCase } from '@/lib/platform/hooks';

export default function DisputesPage() {
  const { primary } = usePrimaryCase();
  const detailQuery = usePortalCaseDetail(primary?.id);
  const disputeAccounts = detailQuery.data?.dispute_accounts ?? {};
  const entries = Object.entries(disputeAccounts);

  return (
    <div>
      <PageHeader
        eyebrow="Disputes"
        title="Dispute account summary"
        description="Counts by dispute status from your primary case on the shared platform. Filing remains staff-mediated."
      />

      <div className="mb-6 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900 dark:text-white/80">
        Lending Readiness Partners does not guarantee removals, score increases, or loan approval.
        Dispute work is operated by staff on your case record.
      </div>

      {!primary ? (
        <p className="text-sm text-slate-500">No case available.</p>
      ) : detailQuery.isLoading ? (
        <p className="text-sm text-slate-500">Loading dispute summary…</p>
      ) : entries.length === 0 ? (
        <PortalCard>
          <p className="text-sm text-slate-500">
            No dispute-status accounts are currently flagged on <strong>{primary.title}</strong>.
          </p>
        </PortalCard>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {entries.map(([status, count]) => (
            <PortalCard key={status}>
              <StatusPill tone="info">{status.replaceAll('_', ' ')}</StatusPill>
              <p className="mt-4 text-3xl font-semibold tabular-nums">{count}</p>
              <p className="mt-1 text-sm text-slate-500">Accounts on primary case</p>
            </PortalCard>
          ))}
        </div>
      )}
    </div>
  );
}
