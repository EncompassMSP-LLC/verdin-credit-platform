'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill, StatTile } from '@/components/portal/PortalCard';
import { usePrimaryCase } from '@/lib/platform/hooks';
import { usePortalCreditAnalysis } from '@/lib/platform/analysis-hooks';
import { usePortalInsights } from '@/lib/platform/readiness-hooks';
import { formatDate } from '@/lib/utils';

export default function AiAnalysisPage() {
  const { primary } = usePrimaryCase();
  const analysisQuery = usePortalCreditAnalysis(primary?.id);
  const insightsQuery = usePortalInsights(primary?.id);
  const analysis = analysisQuery.data;
  const fallbackInsights = insightsQuery.data?.items ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="AI Credit Analysis"
        title="Assistive analysis with human oversight"
        description="Orchestrated Metro 2, FCRA, identity-theft, utilization, and tradeline audits feed your Borrower Readiness Score. Advisors review sensitive steps. Not underwriting advice or an approval decision."
      />

      {!primary ? (
        <p className="rounded-brand border border-navy-900/10 bg-sand-50 px-4 py-3 text-sm text-slate-600 dark:border-white/10 dark:bg-navy-900/40 dark:text-white/70">
          Link a case to your client record to view credit analysis.
        </p>
      ) : analysisQuery.isLoading ? (
        <p className="text-sm text-slate-500">Loading analysis…</p>
      ) : analysisQuery.isError || !analysis ? (
        <div className="space-y-4">
          <p className="rounded-brand border border-navy-900/10 bg-sand-50 px-4 py-3 text-sm text-slate-600 dark:border-white/10 dark:bg-navy-900/40 dark:text-white/70">
            No staff-generated credit analysis run is available yet. Showing persisted account
            intelligence insights when present. Ask your advisor to run credit analysis after
            uploading Equifax, Experian, and TransUnion reports.
          </p>
          {fallbackInsights.length === 0 ? (
            <PortalCard>
              <p className="text-sm text-slate-500">No insights available yet.</p>
            </PortalCard>
          ) : (
            <div className="grid gap-4 lg:grid-cols-3">
              {fallbackInsights.map((insight) => (
                <PortalCard key={insight.id}>
                  <StatusPill tone="info">AI assist</StatusPill>
                  <h2 className="mt-4 text-lg font-semibold">{insight.title}</h2>
                  <p className="mt-2 text-sm text-slate-500">{insight.summary}</p>
                </PortalCard>
              ))}
            </div>
          )}
        </div>
      ) : (
        <>
          <p className="mb-4 text-xs text-slate-500">{analysis.disclaimer}</p>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <StatTile
              label="Borrower Readiness Score™"
              value={`${analysis.borrower_readiness.overall ?? '—'}`}
              hint={analysis.borrower_readiness.band}
              tone="good"
            />
            <StatTile
              label="Mortgage readiness"
              value={`${analysis.mortgage_readiness.overall ?? '—'}`}
              hint={
                analysis.mortgage_readiness.estimated_ready_weeks
                  ? `~${analysis.mortgage_readiness.estimated_ready_weeks} weeks est.`
                  : analysis.mortgage_readiness.band
              }
            />
            <StatTile
              label="Metro 2 / FCRA"
              value={`${analysis.compliance_summary.metro2_total}/${analysis.compliance_summary.fcra_total}`}
              hint="Finding counts"
            />
            <StatTile
              label="Identity indicators"
              value={`${analysis.compliance_summary.identity_theft_total}`}
              hint={`Updated ${formatDate(analysis.generated_at)}`}
            />
          </div>

          <div className="mt-6 grid gap-6 xl:grid-cols-2">
            <PortalCard title="Borrower action plan">
              <ul className="space-y-3">
                {(analysis.borrower_action_plan.items ?? []).map((item) => (
                  <li
                    key={item.title}
                    className="rounded-brand border border-navy-900/8 bg-sand-50 p-3 dark:border-white/10 dark:bg-navy-900/40"
                  >
                    <StatusPill tone={item.priority === 'High' ? 'warn' : 'info'}>
                      {item.priority}
                    </StatusPill>
                    <p className="mt-2 font-medium">{item.title}</p>
                    <p className="mt-1 text-sm text-slate-500">{item.action}</p>
                  </li>
                ))}
              </ul>
            </PortalCard>

            <PortalCard title="Dispute recommendations">
              <ul className="space-y-3">
                {analysis.dispute_recommendations.items.length === 0 ? (
                  <li className="text-sm text-slate-500">No recommendations in this run.</li>
                ) : (
                  analysis.dispute_recommendations.items.map((item, index) => (
                    <li key={`${item.creditor}-${index}`} className="text-sm">
                      <p className="font-medium">
                        {item.creditor} · {item.bureau}
                      </p>
                      <p className="text-slate-500">{item.recommended_action}</p>
                    </li>
                  ))
                )}
              </ul>
            </PortalCard>
          </div>

          <PortalCard className="mt-6" title="Analysis timeline">
            <ol className="space-y-3">
              {analysis.timeline.map((event) => (
                <li key={`${event.at}-${event.title}`} className="flex gap-3 text-sm">
                  <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gold-500" />
                  <div>
                    <p className="font-medium">{event.title}</p>
                    <p className="text-slate-500">{event.detail}</p>
                  </div>
                </li>
              ))}
            </ol>
          </PortalCard>
        </>
      )}
    </div>
  );
}
