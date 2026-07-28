'use client';

import { STAGE_LABELS, useRealtorReferrals } from '@/lib/realtor/portal-hooks';
import { useRealtorAuth } from '@/lib/realtor/auth';

const DEMO_ROWS = [
  {
    referral_id: 'demo-1',
    borrower_initials: 'J.S.',
    pipeline_stage: 'near_ready',
    referral_status: 'in_progress',
    days_in_stage: 4,
    source_label: 'Open house',
    is_own_referral: true,
    created_at: new Date().toISOString(),
  },
  {
    referral_id: 'demo-2',
    borrower_initials: 'A.M.',
    pipeline_stage: 'intake',
    referral_status: 'accepted',
    days_in_stage: 2,
    source_label: 'LO warm handoff',
    is_own_referral: true,
    created_at: new Date().toISOString(),
  },
];

export default function RealtorReferralsPage() {
  const { authMode } = useRealtorAuth();
  const query = useRealtorReferrals();
  const rows = authMode === 'platform' ? (query.data ?? []) : DEMO_ROWS;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-navy-900">My referrals</h1>
        <p className="mt-2 max-w-xl text-sm text-slate-500">
          Partnership-scoped borrower initials and coarse stage only. No tradelines, dispute
          letters, or readiness exports.
        </p>
      </div>

      {query.isLoading && authMode === 'platform' ? (
        <p className="text-sm text-slate-500">Loading referrals…</p>
      ) : null}
      {query.isError && authMode === 'platform' ? (
        <p className="rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-sm text-critical">
          Could not load referrals.
        </p>
      ) : null}

      <div className="overflow-x-auto rounded-md border border-lrp-border bg-lrp-surface-elevated">
        <table className="min-w-full text-left text-sm">
          <thead className="border-b border-lrp-border text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3 font-medium">Borrower</th>
              <th className="px-4 py-3 font-medium">Stage</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Days</th>
              <th className="px-4 py-3 font-medium">Source</th>
              <th className="px-4 py-3 font-medium">Attrib.</th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-slate-500">
                  No referrals yet for this partnership.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.referral_id} className="border-b border-lrp-border/70 last:border-0">
                  <td className="px-4 py-3 font-medium text-navy-900">{row.borrower_initials}</td>
                  <td className="px-4 py-3">
                    {STAGE_LABELS[row.pipeline_stage] ?? row.pipeline_stage}
                  </td>
                  <td className="px-4 py-3 capitalize">
                    {row.referral_status.replaceAll('_', ' ')}
                  </td>
                  <td className="px-4 py-3">{row.days_in_stage}</td>
                  <td className="px-4 py-3 text-slate-500">{row.source_label ?? '—'}</td>
                  <td className="px-4 py-3">{row.is_own_referral ? 'Yours' : 'Team'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
