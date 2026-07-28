'use client';

import { useState } from 'react';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import {
  useCreateWeeklyDigestSubscription,
  useCrmPartnerships,
  useProcessWeeklyDigests,
  useUpdateWeeklyDigestSubscription,
  useWeeklyDigestRuns,
  useWeeklyDigestSubscriptions,
} from '@/lib/crm/partner-hooks';

export default function CrmWeeklyDigestsPage() {
  const { authMode, can } = useCrmAuth();
  const partnershipsQuery = useCrmPartnerships();
  const subsQuery = useWeeklyDigestSubscriptions();
  const runsQuery = useWeeklyDigestRuns();
  const createSub = useCreateWeeklyDigestSubscription();
  const updateSub = useUpdateWeeklyDigestSubscription();
  const processDigests = useProcessWeeklyDigests();

  const [partnershipId, setPartnershipId] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const live =
    authMode === 'platform' && subsQuery.data !== undefined && runsQuery.data !== undefined;
  const usingDemo = !live;
  const partnerships = partnershipsQuery.data ?? [];
  const selectedPartnership = partnershipId || partnerships[0]?.id || '';

  return (
    <RoleGate
      permission="reporting.view"
      fallback={<p className="text-sm text-slate-500">No access to weekly digests.</p>}
    >
      <PageHeader
        eyebrow="Insights"
        title="Weekly digests"
        description="Opt-in partner status digests with PII-minimized pipeline snapshots (LRP-207). Claim-safe only — no approvals or score claims."
      />
      {usingDemo ? (
        <p className="mb-3 text-xs text-slate-500">
          Sign in with platform auth to manage live weekly digest subscriptions and archive runs.
        </p>
      ) : null}

      {!usingDemo && can('reporting.export') ? (
        <div className="mb-6 space-y-4 rounded-md border border-navy-900/10 bg-white p-4 dark:border-white/10 dark:bg-navy-800">
          <div className="flex flex-wrap items-end gap-3">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-slate-600">Partnership</span>
              <select
                className="rounded-md border border-navy-900/15 px-2 py-1.5 dark:border-white/15 dark:bg-navy-900"
                value={selectedPartnership}
                onChange={(e) => setPartnershipId(e.target.value)}
              >
                {partnerships.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.display_name}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-slate-600">Recipient name</span>
              <input
                className="rounded-md border border-navy-900/15 px-2 py-1.5 dark:border-white/15 dark:bg-navy-900"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-slate-600">Email</span>
              <input
                type="email"
                className="rounded-md border border-navy-900/15 px-2 py-1.5 dark:border-white/15 dark:bg-navy-900"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>
            <button
              type="button"
              className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 dark:border-white/15 dark:hover:bg-navy-700"
              disabled={
                createSub.isPending || !selectedPartnership || !name.trim() || !email.trim()
              }
              onClick={() =>
                createSub.mutate(
                  {
                    partnership_id: selectedPartnership,
                    recipient_name: name.trim(),
                    recipient_email: email.trim(),
                    marketing_opt_in: true,
                    send_weekday: 1,
                  },
                  {
                    onSuccess: () => {
                      setName('');
                      setEmail('');
                    },
                  },
                )
              }
            >
              {createSub.isPending ? 'Saving…' : 'Add subscription'}
            </button>
            <button
              type="button"
              className="rounded-md border border-navy-900/15 px-3 py-1.5 text-sm font-medium hover:bg-slate-50 disabled:opacity-50 dark:border-white/15 dark:hover:bg-navy-700"
              disabled={processDigests.isPending}
              onClick={() => processDigests.mutate()}
            >
              {processDigests.isPending ? 'Processing…' : 'Process weekly digests'}
            </button>
          </div>
          {processDigests.isSuccess ? (
            <p className="text-xs text-slate-500">
              Week {processDigests.data.week_key}: processed {processDigests.data.processed_count}{' '}
              run(s).
            </p>
          ) : null}
        </div>
      ) : null}

      <h2 className="mb-2 text-sm font-semibold">Subscriptions</h2>
      <div className="mb-8 rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={subsQuery.data ?? []}
          columns={[
            {
              key: 'recipient',
              header: 'Recipient',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.recipient_name}</p>
                  <p className="text-xs text-slate-500">{r.recipient_email}</p>
                </div>
              ),
            },
            {
              key: 'enabled',
              header: 'State',
              cell: (r) =>
                can('reporting.export') ? (
                  <button
                    type="button"
                    className="text-sm underline decoration-slate-300 underline-offset-2"
                    disabled={updateSub.isPending}
                    onClick={() =>
                      updateSub.mutate({
                        subscriptionId: r.id,
                        body: { enabled: !r.enabled },
                      })
                    }
                  >
                    {r.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                ) : r.enabled ? (
                  'Enabled'
                ) : (
                  'Disabled'
                ),
            },
            {
              key: 'weekday',
              header: 'Send day',
              cell: (r) => `ISO ${r.send_weekday}`,
            },
          ]}
        />
      </div>

      <h2 className="mb-2 text-sm font-semibold">Archive runs</h2>
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={runsQuery.data ?? []}
          columns={[
            { key: 'week', header: 'Week', cell: (r) => r.week_key },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            {
              key: 'attempted',
              header: 'Attempted',
              cell: (r) => new Date(r.attempted_at).toLocaleString(),
            },
            {
              key: 'total',
              header: 'Referrals',
              cell: (r) =>
                String((r.payload as { total_referrals?: number }).total_referrals ?? '—'),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
