import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseDisputeStrategy,
  type AccountDisputeStrategy,
  type DisputeStrategyStage,
  type DisputeStrategySummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';

function SummaryBadges({ summary }: { summary: DisputeStrategySummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.accounts_planned} accounts</Badge>
      <Badge variant="default">{summary.issues_covered} issues</Badge>
      <Badge variant="danger">{summary.high_strength_accounts} high-strength</Badge>
      <Badge variant="warning">{summary.cfpb_recommended} CFPB</Badge>
      <Badge variant="info">{summary.attorney_recommended} preserve</Badge>
    </div>
  );
}

function StageRow({ stage }: { stage: DisputeStrategyStage }) {
  return (
    <li className="rounded-md border border-gray-100 bg-gray-50 px-3 py-2">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <p className="text-sm font-medium text-gray-900">
          Stage {stage.stage_order}: {stage.title}
        </p>
        <Badge variant={stage.recommended ? 'success' : 'default'}>
          {stage.recommended ? 'Recommended' : 'Optional'}
        </Badge>
      </div>
      <p className="mt-1 text-sm text-gray-700">{stage.objective}</p>
      <p className="mt-1 text-xs text-gray-500">{stage.rationale}</p>
      {stage.evidence_hints.length > 0 ? (
        <p className="mt-1 text-xs text-gray-400">Hints: {stage.evidence_hints.join(' · ')}</p>
      ) : null}
    </li>
  );
}

function AccountStrategyCard({ strategy }: { strategy: AccountDisputeStrategy }) {
  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">
            {strategy.creditor_name ?? 'Unknown creditor'}
            {strategy.account_number_masked ? ` · ${strategy.account_number_masked}` : ''}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            {strategy.bureau ? `${strategy.bureau} · ` : ''}
            {strategy.issue_count} issue(s)
            {strategy.primary_rule_ids.length > 0
              ? ` · ${strategy.primary_rule_ids.slice(0, 2).join(', ')}`
              : ''}
          </p>
        </div>
        <Badge
          variant={
            strategy.top_score >= 85 ? 'danger' : strategy.top_score >= 70 ? 'warning' : 'info'
          }
        >
          top {strategy.top_score}/100
        </Badge>
      </div>
      <p className="mt-2 text-xs text-gray-500">{strategy.summary}</p>
      <ul className="mt-3 space-y-2">
        {strategy.stages.map((stage) => (
          <StageRow key={stage.stage_kind} stage={stage} />
        ))}
      </ul>
    </li>
  );
}

export function CaseDisputeStrategyPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const strategyQuery = useQuery({
    queryKey: ['case-dispute-strategy', caseId],
    queryFn: () => getCaseDisputeStrategy(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Dispute strategy">
        <p className="text-sm text-gray-500">
          Multi-stage investigator plan grounded in litigation-strength rankings: CRA dispute →
          furnisher follow-up → CFPB if warranted → preserve for attorney consult. Not legal advice;
          does not auto-file.
        </p>

        {strategyQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading dispute strategy…</p>
        ) : null}

        {strategyQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {strategyQuery.error instanceof ApiClientError && strategyQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : strategyQuery.error instanceof Error
                ? strategyQuery.error.message
                : 'Failed to load dispute strategy'}
          </p>
        ) : null}

        {strategyQuery.data ? (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">{strategyQuery.data.disclaimer}</p>
              <SummaryBadges summary={strategyQuery.data.summary} />
            </div>

            {strategyQuery.data.strategies.length === 0 ? (
              <p className="text-sm text-gray-500">
                No ranked issues available to plan against yet.
              </p>
            ) : (
              <ul className="space-y-3">
                {strategyQuery.data.strategies.map((strategy) => (
                  <AccountStrategyCard key={strategy.account_key} strategy={strategy} />
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
