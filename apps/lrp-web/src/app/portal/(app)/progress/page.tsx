'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePortalCases } from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

const stageOrder = [
  'intake',
  'review',
  'evidence_gathering',
  'dispute_preparation',
  'awaiting_response',
  'monitoring',
  'complete',
] as const;

const stageLabel: Record<string, string> = {
  intake: 'Intake',
  review: 'Review',
  evidence_gathering: 'Evidence gathering',
  dispute_preparation: 'Dispute preparation',
  awaiting_response: 'Awaiting response',
  monitoring: 'Monitoring',
  complete: 'Complete',
};

export default function ProgressPage() {
  const casesQuery = usePortalCases();
  const primary = casesQuery.data?.[0];
  const currentIndex = primary
    ? Math.max(0, stageOrder.indexOf(primary.stage as (typeof stageOrder)[number]))
    : -1;
  const percent = currentIndex < 0 ? 0 : Math.round(((currentIndex + 1) / stageOrder.length) * 100);

  return (
    <div>
      <PageHeader
        eyebrow="Progress Tracker"
        title="Case stage progress"
        description="Driven by your primary case stage in the shared platform database."
      />

      <PortalCard className="mb-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-eyebrow text-gold-600">Journey completion</p>
            <p className="mt-1 text-3xl font-semibold tabular-nums">{percent}%</p>
            <p className="text-sm text-slate-500 dark:text-white/60">
              {primary
                ? `${primary.title} · ${stageLabel[primary.stage] ?? primary.stage}`
                : 'No primary case'}
            </p>
          </div>
          <div className="h-3 w-full max-w-md overflow-hidden rounded-full bg-sand-200 dark:bg-navy-900">
            <div
              className="h-full rounded-full bg-progress-accent"
              style={{ width: `${percent}%` }}
            />
          </div>
        </div>
      </PortalCard>

      <ol className="space-y-3">
        {stageOrder.map((stage, index) => {
          const complete = currentIndex >= index;
          return (
            <li key={stage}>
              <PortalCard>
                <div className="flex items-start gap-4">
                  <span
                    className={
                      complete
                        ? 'flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-sm font-bold text-white'
                        : 'flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sand-200 text-sm font-bold text-slate-500 dark:bg-navy-900'
                    }
                  >
                    {index + 1}
                  </span>
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h2 className="font-semibold">{stageLabel[stage]}</h2>
                      <StatusPill tone={complete ? 'good' : 'neutral'}>
                        {complete ? 'Reached' : 'Upcoming'}
                      </StatusPill>
                    </div>
                    {primary && primary.stage === stage ? (
                      <p className="mt-1 text-sm text-slate-500">
                        Current stage · updated {formatDate(primary.updated_at)}
                      </p>
                    ) : null}
                  </div>
                </div>
              </PortalCard>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
