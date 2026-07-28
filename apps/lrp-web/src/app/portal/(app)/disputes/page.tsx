'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import {
  usePortalCaseDetail,
  usePortalDisputeStrategySuggestions,
  usePrimaryCase,
} from '@/lib/platform/hooks';
import { formatDate } from '@/lib/utils';

export default function DisputesPage() {
  const { primary } = usePrimaryCase();
  const detailQuery = usePortalCaseDetail(primary?.id);
  const suggestionsQuery = usePortalDisputeStrategySuggestions(primary?.id);
  const disputeAccounts = detailQuery.data?.dispute_accounts ?? {};
  const entries = Object.entries(disputeAccounts);
  const suggestions = suggestionsQuery.data;

  return (
    <div>
      <PageHeader
        eyebrow="Disputes"
        title="Dispute account summary"
        description="Counts by dispute status from your primary case on the shared platform. Filing remains staff-mediated."
      />

      <div className="mb-6 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900 dark:text-white/80">
        Lending Readiness Partners does not guarantee removals, score increases, or loan approval.
        Dispute work is operated by staff on your case record — suggestions below never file
        automatically.
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

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-navy-900 dark:text-white">
          Advisory strategy suggestions
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Staff-reviewed next steps from your readiness team. Not legal advice; never auto-sent.
        </p>

        {!primary ? null : suggestionsQuery.isLoading ? (
          <p className="mt-4 text-sm text-slate-500">Loading suggestions…</p>
        ) : suggestionsQuery.isError ? (
          <p className="mt-4 text-sm text-slate-500">
            Suggestions are unavailable right now. Ask your advisor for the latest plan.
          </p>
        ) : !suggestions || suggestions.suggestions.length === 0 ? (
          <PortalCard className="mt-4">
            <p className="text-sm text-slate-500">
              No shared dispute strategy yet. When your team publishes a plan, advisory suggestions
              appear here — still staff-mediated for any letters.
            </p>
          </PortalCard>
        ) : (
          <div className="mt-4 space-y-4">
            <p className="text-xs text-slate-500">{suggestions.disclaimer}</p>
            {suggestions.generated_at ? (
              <p className="text-xs text-slate-400">
                Shared {formatDate(suggestions.generated_at, { dateStyle: 'medium' })}
              </p>
            ) : null}
            {suggestions.suggestions.map((item) => (
              <PortalCard key={`${item.creditor_label}-${item.account_number_masked ?? 'acct'}`}>
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <div>
                    <p className="text-sm font-semibold text-navy-900 dark:text-white">
                      {item.creditor_label}
                      {item.account_number_masked ? (
                        <span className="ml-2 font-normal text-slate-500">
                          {item.account_number_masked}
                        </span>
                      ) : null}
                    </p>
                    <p className="mt-1 text-sm text-slate-600 dark:text-white/70">{item.summary}</p>
                  </div>
                  {item.recommended_stage_titles.length > 0 ? (
                    <StatusPill tone="info">
                      {item.recommended_stage_titles.length} recommended
                    </StatusPill>
                  ) : null}
                </div>
                <ul className="mt-4 space-y-2">
                  {item.stages.map((stage) => (
                    <li
                      key={`${stage.stage_kind}-${stage.title}`}
                      className="rounded-md border border-navy-900/10 px-3 py-2 text-sm dark:border-white/10"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-medium text-navy-900 dark:text-white">
                          {stage.title}
                        </span>
                        {stage.recommended ? <StatusPill tone="good">Suggested</StatusPill> : null}
                      </div>
                      {stage.objective ? (
                        <p className="mt-1 text-xs text-slate-500">{stage.objective}</p>
                      ) : null}
                    </li>
                  ))}
                </ul>
              </PortalCard>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
