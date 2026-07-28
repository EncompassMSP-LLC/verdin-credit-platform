'use client';

import Link from 'next/link';
import { useRealtorAuth } from '@/lib/realtor/auth';

export default function RealtorDashboardPage() {
  const { user, authMode } = useRealtorAuth();

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-600">Overview</p>
        <h1 className="mt-1 text-2xl font-semibold text-navy-900">
          Welcome{user ? `, ${user.displayName}` : ''}
        </h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-500">
          You are signed into the realtor partner realm for{' '}
          <span className="font-medium text-navy-900">{user?.partnershipDisplayName}</span>. This
          workspace is isolated from lender, borrower portal, and staff CRM shells.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-md border border-lrp-border bg-lrp-surface-elevated p-5">
          <h2 className="text-sm font-semibold text-navy-900">Session</h2>
          <dl className="mt-3 space-y-2 text-sm text-slate-600">
            <div className="flex justify-between gap-4">
              <dt>Organization</dt>
              <dd className="text-right font-medium text-navy-900">{user?.organizationName}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>Auth mode</dt>
              <dd className="text-right font-medium text-navy-900">{authMode ?? '—'}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt>Permissions</dt>
              <dd className="text-right font-medium text-navy-900">
                {user?.permissions.join(', ')}
              </dd>
            </div>
          </dl>
        </div>
        <div className="rounded-md border border-lrp-border bg-lrp-surface-elevated p-5">
          <h2 className="text-sm font-semibold text-navy-900">Next: portal MVP</h2>
          <p className="mt-2 text-sm text-slate-500">
            Referral list and coarse pipeline status land in LRP-302. Navigation stubs are gated to
            realtor permissions only.
          </p>
          <div className="mt-4 flex flex-wrap gap-3 text-sm">
            <Link href="/realtor/referrals" className="font-medium text-gold-700 hover:underline">
              My referrals →
            </Link>
            <Link href="/realtor/pipeline" className="font-medium text-gold-700 hover:underline">
              Coarse status →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
