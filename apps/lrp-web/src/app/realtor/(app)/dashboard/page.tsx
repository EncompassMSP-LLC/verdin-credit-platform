'use client';

import Link from 'next/link';
import { useRealtorAuth } from '@/lib/realtor/auth';
import { STAGE_LABELS, useRealtorPortalDashboard } from '@/lib/realtor/portal-hooks';

const DEMO_SUMMARY = {
  total_referrals: 3,
  own_referral_count: 2,
  near_ready_count: 1,
  mortgage_ready_count: 0,
  partnership_display_name: 'Summit × LRP',
  recent: [
    {
      referral_id: 'demo-1',
      borrower_initials: 'J.S.',
      pipeline_stage: 'near_ready',
      referral_status: 'in_progress',
      days_in_stage: 4,
      is_own_referral: true,
    },
    {
      referral_id: 'demo-2',
      borrower_initials: 'A.M.',
      pipeline_stage: 'intake',
      referral_status: 'accepted',
      days_in_stage: 2,
      is_own_referral: true,
    },
  ],
  advisory_disclaimer:
    'Lending Readiness Score™ and pipeline status are advisory organizing tools. They are not credit scores from a consumer reporting agency, not underwriting decisions, and not guarantees of loan approval or terms.',
};

export default function RealtorDashboardPage() {
  const { user, authMode } = useRealtorAuth();
  const dashboard = useRealtorPortalDashboard();

  const data =
    authMode === 'platform' && dashboard.data
      ? dashboard.data
      : authMode === 'demo'
        ? {
            ...DEMO_SUMMARY,
            partnership_display_name:
              user?.partnershipDisplayName ?? DEMO_SUMMARY.partnership_display_name,
          }
        : null;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">Overview</p>
        <h1 className="mt-1 text-2xl font-semibold text-navy-900">
          Welcome{user ? `, ${user.displayName}` : ''}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-500">
          Coarse status for{' '}
          <span className="font-medium text-navy-900">
            {data?.partnership_display_name ?? user?.partnershipDisplayName}
          </span>
          . Full tradelines, dispute letters, and lender underwriting surfaces stay out of this
          realm.
        </p>
      </div>

      {dashboard.isLoading && authMode === 'platform' ? (
        <p className="text-sm text-slate-500">Loading partnership summary…</p>
      ) : null}
      {dashboard.isError && authMode === 'platform' ? (
        <p className="rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-sm text-critical">
          Could not load realtor dashboard. Confirm your membership is active.
        </p>
      ) : null}

      {data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: 'Referrals', value: data.total_referrals },
              { label: 'Attributed to you', value: data.own_referral_count },
              { label: 'Near ready', value: data.near_ready_count },
              { label: 'Mortgage ready', value: data.mortgage_ready_count },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-md border border-lrp-border bg-lrp-surface-elevated p-4"
              >
                <p className="text-xs uppercase tracking-wide text-slate-500">{stat.label}</p>
                <p className="mt-2 text-2xl font-semibold text-navy-900">{stat.value}</p>
              </div>
            ))}
          </div>

          <div className="rounded-md border border-lrp-border bg-lrp-surface-elevated p-5">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-sm font-semibold text-navy-900">Recent activity</h2>
              <Link
                href="/realtor/referrals"
                className="text-sm font-medium text-gold-700 hover:underline"
              >
                View all →
              </Link>
            </div>
            <ul className="mt-4 divide-y divide-lrp-border">
              {data.recent.length === 0 ? (
                <li className="py-3 text-sm text-slate-500">
                  No referrals in this partnership yet.
                </li>
              ) : (
                data.recent.map((row) => (
                  <li
                    key={row.referral_id}
                    className="flex items-center justify-between gap-3 py-3 text-sm"
                  >
                    <div>
                      <p className="font-medium text-navy-900">{row.borrower_initials}</p>
                      <p className="text-xs text-slate-500">
                        {STAGE_LABELS[row.pipeline_stage] ?? row.pipeline_stage}
                        {row.is_own_referral ? ' · yours' : ''}
                      </p>
                    </div>
                    <p className="text-xs text-slate-500">{row.days_in_stage}d in stage</p>
                  </li>
                ))
              )}
            </ul>
          </div>

          <p className="text-xs leading-relaxed text-slate-500">{data.advisory_disclaimer}</p>
        </>
      ) : null}
    </div>
  );
}
