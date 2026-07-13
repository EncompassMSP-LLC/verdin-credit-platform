import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseAttorneyChecklist,
  getCaseCfpbChecklist,
  getCaseDisputeStrategy,
  prepareCaseDisputeStrategyStage,
  type AccountAttorneyChecklist,
  type AccountCfpbChecklist,
  type AccountDisputeStrategy,
  type DisputeStrategyStage,
  type DisputeStrategyStageKind,
  type DisputeStrategySummary,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

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

function ChecklistAccount({
  account,
  accent,
}: {
  account: AccountCfpbChecklist | AccountAttorneyChecklist;
  accent: 'amber' | 'slate';
}) {
  const border =
    accent === 'amber' ? 'border-amber-200 bg-amber-50/40' : 'border-slate-200 bg-slate-50/40';
  const escalation =
    'attorney_escalation' in account && account.attorney_escalation ? (
      <Badge variant="danger">escalation</Badge>
    ) : null;
  return (
    <li className={`rounded-md border ${border} px-3 py-2`}>
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-sm font-medium text-gray-900">
          {account.creditor_name ?? 'Unknown creditor'}
          {account.account_number_masked ? ` · ${account.account_number_masked}` : ''}
          <span className="ml-2 text-xs font-normal text-gray-500">
            top {account.top_score}/100
          </span>
        </p>
        {escalation}
      </div>
      <ul className="mt-2 space-y-1">
        {account.items.map((item) => (
          <li key={item.item_id} className="text-xs text-gray-700">
            <span className="font-medium">
              {item.required ? 'Required' : 'Optional'} · {item.category}:
            </span>{' '}
            {item.title}
            <span className="block text-gray-500">{item.detail}</span>
          </li>
        ))}
      </ul>
    </li>
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
  const queryClient = useQueryClient();
  const strategyQuery = useQuery({
    queryKey: ['case-dispute-strategy', caseId],
    queryFn: () => getCaseDisputeStrategy(caseId),
    retry: false,
  });

  const cfpbQuery = useQuery({
    queryKey: ['case-cfpb-checklist', caseId],
    queryFn: () => getCaseCfpbChecklist(caseId),
    enabled: (strategyQuery.data?.summary.cfpb_recommended ?? 0) > 0,
    retry: false,
  });

  const attorneyQuery = useQuery({
    queryKey: ['case-attorney-checklist', caseId],
    queryFn: () => getCaseAttorneyChecklist(caseId),
    enabled: (strategyQuery.data?.summary.attorney_recommended ?? 0) > 0,
    retry: false,
  });

  const prepareMutation = useMutation({
    mutationFn: (
      stage_kind: Extract<DisputeStrategyStageKind, 'cra_dispute' | 'furnisher_dispute'>,
    ) => prepareCaseDisputeStrategyStage(caseId, { stage_kind, recommended_only: true }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['case-accounts', caseId] });
      void queryClient.invalidateQueries({
        queryKey: ['case-credit-report-discrepancies', caseId],
      });
    },
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

            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                loading={prepareMutation.isPending && prepareMutation.variables === 'cra_dispute'}
                onClick={() => prepareMutation.mutate('cra_dispute')}
              >
                Prepare CRA stage letters
              </Button>
              <Button
                size="sm"
                variant="secondary"
                loading={
                  prepareMutation.isPending && prepareMutation.variables === 'furnisher_dispute'
                }
                onClick={() => prepareMutation.mutate('furnisher_dispute')}
              >
                Prepare furnisher stage letters
              </Button>
            </div>

            {prepareMutation.isError ? (
              <p className="text-sm text-red-600">
                {prepareMutation.error instanceof Error
                  ? prepareMutation.error.message
                  : 'Failed to prepare strategy stage letters'}
              </p>
            ) : null}

            {prepareMutation.data ? (
              <div className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700">
                <p>
                  Prepared {prepareMutation.data.prepared.length} letter(s) for{' '}
                  {prepareMutation.data.stage_kind} ({prepareMutation.data.recipient_type}).
                  {prepareMutation.data.match_keys.length > 0
                    ? ` Match keys: ${prepareMutation.data.match_keys.length}.`
                    : ''}
                  {(prepareMutation.data.direct_account_keys?.length ?? 0) > 0
                    ? ` Direct accounts: ${prepareMutation.data.direct_account_keys?.length}.`
                    : ''}
                  {prepareMutation.data.skipped.length > 0
                    ? ` Skipped ${prepareMutation.data.skipped.length}.`
                    : ''}
                </p>
                {prepareMutation.data.note ? (
                  <p className="mt-1 text-xs text-gray-500">{prepareMutation.data.note}</p>
                ) : null}
                {prepareMutation.data.prepared.length > 0 ? (
                  <ul className="mt-2 space-y-1 text-xs">
                    {prepareMutation.data.prepared.map((item) => (
                      <li key={item.match_key}>
                        {item.creditor_name}
                        {item.dispute_letter_id ? (
                          <>
                            {' · '}
                            <Link
                              to={`/accounts/${item.account_id}`}
                              className="text-brand-600 hover:underline"
                            >
                              open account
                            </Link>
                          </>
                        ) : null}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            ) : null}

            {cfpbQuery.data && cfpbQuery.data.accounts.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-900">CFPB escalation checklist</p>
                <p className="text-xs text-gray-500">{cfpbQuery.data.disclaimer}</p>
                <p className="text-xs text-gray-500">
                  {cfpbQuery.data.summary.accounts_listed} account(s) ·{' '}
                  {cfpbQuery.data.summary.required_items} required ·{' '}
                  {cfpbQuery.data.summary.optional_items} optional
                </p>
                <ul className="space-y-2">
                  {cfpbQuery.data.accounts.map((account) => (
                    <ChecklistAccount key={account.account_key} account={account} accent="amber" />
                  ))}
                </ul>
              </div>
            ) : null}

            {attorneyQuery.data && attorneyQuery.data.accounts.length > 0 ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-900">Attorney-preserve checklist</p>
                <p className="text-xs text-gray-500">{attorneyQuery.data.disclaimer}</p>
                <p className="text-xs text-gray-500">
                  {attorneyQuery.data.summary.accounts_listed} account(s) ·{' '}
                  {attorneyQuery.data.summary.required_items} required ·{' '}
                  {attorneyQuery.data.summary.optional_items} optional ·{' '}
                  {attorneyQuery.data.summary.escalation_flagged} escalation-flagged
                </p>
                <ul className="space-y-2">
                  {attorneyQuery.data.accounts.map((account) => (
                    <ChecklistAccount key={account.account_key} account={account} accent="slate" />
                  ))}
                </ul>
              </div>
            ) : null}

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
