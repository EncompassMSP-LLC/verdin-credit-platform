'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatTile } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { analytics } from '@/lib/lender/data';
import { STAGE_LABELS } from '@/lib/lender/nav';

function BarChart({
  items,
  labelKey,
  valueKey,
}: {
  items: Array<Record<string, string | number>>;
  labelKey: string;
  valueKey: string;
}) {
  const max = Math.max(...items.map((item) => Number(item[valueKey])), 1);

  return (
    <div className="space-y-3">
      {items.map((item) => {
        const value = Number(item[valueKey]);
        const pct = Math.round((value / max) * 100);
        return (
          <div key={String(item[labelKey])}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="font-medium text-navy-900 dark:text-white">
                {String(item[labelKey])}
              </span>
              <span className="tabular-nums text-slate-500">{value}</span>
            </div>
            <div className="h-2 overflow-hidden rounded-md bg-navy-900/10 dark:bg-white/10">
              <div
                className="h-full rounded-md bg-[#00133E] dark:bg-gold-500"
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default function AnalyticsPage() {
  const stageItems = analytics.stageDistribution
    .filter((item) => item.count > 0)
    .map((item) => ({
      label: STAGE_LABELS[item.stage] ?? item.stage,
      count: item.count,
    }));

  const trendMax = Math.max(
    ...analytics.monthlyTrend.flatMap((m) => [m.referred, m.ready, m.funded]),
    1,
  );

  return (
    <RoleGate permission="analytics.view">
      <div>
        <PageHeader
          eyebrow="Analytics"
          title="Partner performance"
          description={`Operational metrics for ${analytics.periodLabel}. Advisory readiness bands—not approval or funding guarantees.`}
        />

        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <StatTile
            label="Referrals accepted"
            value={`${analytics.referralsAccepted}`}
            hint={analytics.periodLabel}
          />
          <StatTile
            label="Avg days to near ready"
            value={`${analytics.avgDaysToNearReady}`}
            hint="Remediation cycle time"
          />
          <StatTile
            label="Mortgage-ready"
            value={`${analytics.mortgageReadyCount}`}
            hint="Advisory band threshold"
            tone="good"
          />
          <StatTile
            label="Pull-through"
            value={`${Math.round(analytics.pullThroughRate * 100)}%`}
            hint={`${analytics.fundedCount} funded`}
          />
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-2">
          <PortalCard
            title="Stage distribution"
            description="Active demo cohort by pipeline stage."
          >
            <BarChart
              items={stageItems.map((item) => ({ label: item.label, count: item.count }))}
              labelKey="label"
              valueKey="count"
            />
          </PortalCard>

          <PortalCard title="Readiness bands" description="Advisory composite distribution.">
            <BarChart
              items={analytics.readinessBands.map((item) => ({
                label: item.band,
                count: item.count,
              }))}
              labelKey="label"
              valueKey="count"
            />
          </PortalCard>
        </div>

        <PortalCard
          className="mt-6"
          title="Monthly trend"
          description="Referred vs ready vs funded (trailing six months)."
        >
          <div className="space-y-4">
            {analytics.monthlyTrend.map((month) => (
              <div key={month.month}>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  {month.month}
                </p>
                <div className="grid gap-2 sm:grid-cols-3">
                  {(
                    [
                      {
                        label: 'Referred',
                        value: month.referred,
                        className: 'bg-navy-900 dark:bg-navy-700',
                      },
                      { label: 'Ready', value: month.ready, className: 'bg-gold-500' },
                      { label: 'Funded', value: month.funded, className: 'bg-emerald-600' },
                    ] as const
                  ).map((metric) => (
                    <div key={metric.label}>
                      <div className="mb-1 flex justify-between text-[0.65rem] text-slate-500">
                        <span>{metric.label}</span>
                        <span className="tabular-nums">{metric.value}</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-md bg-navy-900/10 dark:bg-white/10">
                        <div
                          className={`h-full rounded-md ${metric.className}`}
                          style={{ width: `${Math.round((metric.value / trendMax) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
