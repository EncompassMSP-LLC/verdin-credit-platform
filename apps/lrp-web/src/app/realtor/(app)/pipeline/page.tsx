'use client';

import { STAGE_LABELS, useRealtorPipeline } from '@/lib/realtor/portal-hooks';
import { useRealtorAuth } from '@/lib/realtor/auth';

const STAGES = [
  'referred',
  'intake',
  'in_repair',
  'near_ready',
  'mortgage_ready',
  'in_underwriting',
  'funded',
  'declined',
  'withdrawn',
] as const;

const DEMO_CARDS = [
  {
    referral_id: 'demo-1',
    borrower_initials: 'J.S.',
    pipeline_stage: 'near_ready',
    days_in_stage: 4,
    is_own_referral: true,
  },
  {
    referral_id: 'demo-2',
    borrower_initials: 'A.M.',
    pipeline_stage: 'intake',
    days_in_stage: 2,
    is_own_referral: true,
  },
  {
    referral_id: 'demo-3',
    borrower_initials: 'R.T.',
    pipeline_stage: 'referred',
    days_in_stage: 1,
    is_own_referral: false,
  },
];

export default function RealtorPipelinePage() {
  const { authMode } = useRealtorAuth();
  const query = useRealtorPipeline();
  const cards = authMode === 'platform' ? (query.data?.cards ?? []) : DEMO_CARDS;
  const title =
    authMode === 'platform'
      ? (query.data?.partnership_display_name ?? 'Coarse status')
      : 'Coarse status';

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold text-navy-900">{title}</h1>
        <p className="mt-2 max-w-xl text-sm text-slate-500">
          Stage board for your realtor partnership. Advisory progress only — not underwriting or
          funding decisions.
        </p>
      </div>

      {query.isLoading && authMode === 'platform' ? (
        <p className="text-sm text-slate-500">Loading pipeline…</p>
      ) : null}

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {STAGES.map((stage) => {
          const stageCards = cards.filter((c) => c.pipeline_stage === stage);
          if (stageCards.length === 0 && authMode === 'platform' && cards.length > 0) {
            return null;
          }
          return (
            <section
              key={stage}
              className="rounded-md border border-lrp-border bg-lrp-surface-elevated p-4"
            >
              <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                {STAGE_LABELS[stage] ?? stage}
              </h2>
              <ul className="mt-3 space-y-2">
                {stageCards.length === 0 ? (
                  <li className="text-xs text-slate-400">None</li>
                ) : (
                  stageCards.map((card) => (
                    <li
                      key={card.referral_id}
                      className="rounded border border-lrp-border/80 bg-lrp-surface px-3 py-2 text-sm"
                    >
                      <p className="font-medium text-navy-900">{card.borrower_initials}</p>
                      <p className="text-xs text-slate-500">
                        {card.days_in_stage}d{card.is_own_referral ? ' · yours' : ''}
                      </p>
                    </li>
                  ))
                )}
              </ul>
            </section>
          );
        })}
      </div>
    </div>
  );
}
