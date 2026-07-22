import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Link, useParams } from 'react-router-dom';
import {
  ApiClientError,
  getCase,
  getCaseDisputeStrategy,
  getCaseLitigationStrength,
  getCaseReinvestigationSummary,
  prepareCaseDisputeStrategyStage,
  type AccountDisputeStrategy,
  type DisputeStrategyStage,
  type DisputeStrategyStageKind,
  type LitigationStrengthIssue,
  type RedisputeAction,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { caseFindingDeepLink } from '../../lib/findingDeepLink';

const STAGE_LABELS: Record<DisputeStrategyStageKind, string> = {
  cra_dispute: 'CRA dispute',
  furnisher_dispute: 'Furnisher follow-up',
  cfpb_escalation: 'CFPB escalation',
  attorney_preserve: 'Attorney preserve',
};

const ACTION_LABELS: Record<RedisputeAction, string> = {
  wait: 'Wait on clock',
  prepare_initial: 'Prepare initial dispute',
  redispute: 'Prepare redispute',
  escalate_cfpb: 'Escalate to CFPB',
  escalate_attorney: 'Preserve for attorney',
  resolved: 'Resolved',
};

function scoreVariant(score: number): 'danger' | 'warning' | 'info' {
  if (score >= 85) return 'danger';
  if (score >= 70) return 'warning';
  return 'info';
}

function recommendedStage(strategy: AccountDisputeStrategy): DisputeStrategyStage | undefined {
  return (
    strategy.stages.find((stage) => stage.recommended) ??
    strategy.stages.slice().sort((a, b) => a.stage_order - b.stage_order)[0]
  );
}

function issuesForStrategy(
  strategy: AccountDisputeStrategy,
  issues: LitigationStrengthIssue[],
): LitigationStrengthIssue[] {
  const sourceIds = new Set(
    strategy.stages.flatMap((stage) => stage.issue_source_ids).filter(Boolean),
  );
  const matched = issues.filter(
    (issue) =>
      sourceIds.has(issue.source_id) ||
      (strategy.match_key != null && issue.match_key === strategy.match_key) ||
      (strategy.creditor_name != null &&
        issue.creditor_name != null &&
        issue.creditor_name.toLowerCase() === strategy.creditor_name.toLowerCase()),
  );
  if (matched.length > 0) {
    return matched.sort((a, b) => a.rank - b.rank);
  }
  return issues
    .filter(
      (issue) =>
        strategy.match_key != null &&
        issue.match_key != null &&
        issue.match_key === strategy.match_key,
    )
    .sort((a, b) => a.rank - b.rank);
}

function StageSteps({ stages }: { stages: DisputeStrategyStage[] }) {
  return (
    <ol className="mt-3 space-y-2">
      {stages
        .slice()
        .sort((a, b) => a.stage_order - b.stage_order)
        .map((stage) => (
          <li
            key={`${stage.stage_order}-${stage.stage_kind}`}
            className={`rounded-md border px-3 py-2 ${
              stage.recommended ? 'border-brand-200 bg-brand-50/40' : 'border-gray-100 bg-white'
            }`}
          >
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-medium text-gray-500">Step {stage.stage_order}</span>
              <span className="text-sm font-medium text-gray-900">
                {STAGE_LABELS[stage.stage_kind]}
              </span>
              {stage.recommended ? <Badge variant="success">best next</Badge> : null}
            </div>
            <p className="mt-1 text-sm text-gray-700">{stage.objective}</p>
            <p className="mt-1 text-xs text-gray-500">{stage.rationale}</p>
            {stage.evidence_hints.length > 0 ? (
              <p className="mt-1 text-xs text-gray-400">
                Evidence: {stage.evidence_hints.join(' · ')}
              </p>
            ) : null}
          </li>
        ))}
    </ol>
  );
}

function AccountPlaybookCard({
  caseId,
  strategy,
  issues,
  pendingPrepareKey,
  onPrepare,
}: {
  caseId: string;
  strategy: AccountDisputeStrategy;
  issues: LitigationStrengthIssue[];
  pendingPrepareKey: string | null;
  onPrepare: (
    stageKind: Extract<DisputeStrategyStageKind, 'cra_dispute' | 'furnisher_dispute'>,
    accountKey: string,
  ) => void;
}) {
  const best = recommendedStage(strategy);
  const linkedIssues = issuesForStrategy(strategy, issues);
  const canPrepare = best?.stage_kind === 'cra_dispute' || best?.stage_kind === 'furnisher_dispute';

  return (
    <li className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            {strategy.creditor_name ?? 'Unknown creditor'}
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            {strategy.account_number_masked ? `${strategy.account_number_masked} · ` : null}
            {strategy.bureau ?? 'bureau unknown'}
            {strategy.match_key ? (
              <span className="ml-2 font-mono text-xs text-gray-400">{strategy.match_key}</span>
            ) : null}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant={scoreVariant(strategy.top_score)}>{strategy.top_score}/100</Badge>
          <Badge variant="default">{strategy.issue_count} issues</Badge>
        </div>
      </div>

      <p className="mt-3 text-sm text-gray-700">{strategy.summary}</p>

      {best ? (
        <div className="mt-3 rounded-md border border-emerald-200 bg-emerald-50/50 px-3 py-2">
          <p className="text-xs font-medium uppercase tracking-wide text-emerald-800">
            Best probable path
          </p>
          <p className="mt-1 text-sm font-medium text-gray-900">
            {STAGE_LABELS[best.stage_kind]} — {best.title}
          </p>
          <p className="mt-1 text-sm text-gray-700">{best.objective}</p>
          {canPrepare ? (
            <div className="mt-2">
              <Button
                size="sm"
                loading={pendingPrepareKey === `${best.stage_kind}:${strategy.account_key}`}
                onClick={() =>
                  onPrepare(
                    best.stage_kind as Extract<
                      DisputeStrategyStageKind,
                      'cra_dispute' | 'furnisher_dispute'
                    >,
                    strategy.account_key,
                  )
                }
              >
                Prepare {STAGE_LABELS[best.stage_kind]} letter draft
              </Button>
            </div>
          ) : (
            <p className="mt-2 text-xs text-gray-600">
              Escalation / preserve stage — use checklists and packets on Case Detail; no auto-file.
            </p>
          )}
        </div>
      ) : null}

      {linkedIssues.length > 0 ? (
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-900">Issues driving this plan</h3>
          <ul className="mt-2 space-y-2">
            {linkedIssues.map((issue) => (
              <li key={issue.source_id} className="rounded-md border border-gray-100 px-3 py-2">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-medium text-gray-900">
                    #{issue.rank} · {issue.title}
                  </span>
                  <Badge variant={scoreVariant(issue.score)}>{issue.score}/100</Badge>
                  <Badge variant="default">{issue.source_kind}</Badge>
                  <Link
                    to={caseFindingDeepLink(caseId, issue.source_kind, issue.source_id)}
                    className="text-xs text-brand-600 hover:underline"
                  >
                    View finding
                  </Link>
                </div>
                <p className="mt-1 text-xs text-gray-500">{issue.rationale}</p>
                {issue.factors.length > 0 ? (
                  <p className="mt-1 text-xs text-gray-400">
                    Why this is strong: {issue.factors.join(', ')}
                  </p>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <details className="mt-4">
        <summary className="cursor-pointer text-sm font-medium text-brand-600">
          Full stage sequence
        </summary>
        <StageSteps stages={strategy.stages} />
      </details>
    </li>
  );
}

export function CaseDisputePlaybookPage() {
  const { caseId } = useParams<{ caseId: string }>();
  const queryClient = useQueryClient();
  const [filter, setFilter] = useState('');

  const caseQuery = useQuery({
    queryKey: ['case', caseId],
    queryFn: () => getCase(caseId!),
    enabled: Boolean(caseId),
  });

  const strategyQuery = useQuery({
    queryKey: ['case-dispute-strategy', caseId],
    queryFn: () => getCaseDisputeStrategy(caseId!),
    enabled: Boolean(caseId),
    retry: false,
  });

  const strengthQuery = useQuery({
    queryKey: ['case-litigation-strength', caseId],
    queryFn: () => getCaseLitigationStrength(caseId!),
    enabled: Boolean(caseId),
    retry: false,
  });

  const summaryQuery = useQuery({
    queryKey: ['case-reinvestigation-summary', caseId],
    queryFn: () => getCaseReinvestigationSummary(caseId!),
    enabled: Boolean(caseId),
    retry: false,
  });

  const prepareMutation = useMutation({
    mutationFn: (input: {
      stage_kind: Extract<DisputeStrategyStageKind, 'cra_dispute' | 'furnisher_dispute'>;
      account_key: string;
    }) =>
      prepareCaseDisputeStrategyStage(caseId!, {
        stage_kind: input.stage_kind,
        account_keys: [input.account_key],
        recommended_only: false,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['case-accounts', caseId] });
    },
  });

  const pendingPrepareKey =
    prepareMutation.isPending && prepareMutation.variables
      ? `${prepareMutation.variables.stage_kind}:${prepareMutation.variables.account_key}`
      : null;

  const strategies = useMemo(() => {
    const rows = strategyQuery.data?.strategies ?? [];
    const q = filter.trim().toLowerCase();
    if (!q) {
      return rows.slice().sort((a, b) => b.top_score - a.top_score);
    }
    return rows
      .filter((row) => {
        const haystack = [
          row.creditor_name,
          row.account_number_masked,
          row.bureau,
          row.match_key,
          row.summary,
          ...row.primary_rule_ids,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return haystack.includes(q);
      })
      .sort((a, b) => b.top_score - a.top_score);
  }, [filter, strategyQuery.data?.strategies]);

  if (!caseId) {
    return null;
  }

  if (caseQuery.isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading dispute playbook…</p>
        </Card>
      </div>
    );
  }

  if (caseQuery.isError || !caseQuery.data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {caseQuery.error instanceof Error ? caseQuery.error.message : 'Case not found'}
            </p>
            <Link to="/cases" className="mt-4 inline-block text-sm text-brand-600 hover:underline">
              Back to cases
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  const caseData = caseQuery.data;

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to={`/cases/${caseId}`} className="text-sm text-brand-600 hover:underline">
            ← Back to case
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Dispute playbook</h1>
          <p className="mt-1 text-sm text-gray-600">
            {caseData.title}
            {caseData.case_number ? ` · ${caseData.case_number}` : null}
          </p>
          <p className="mt-2 max-w-3xl text-sm text-gray-500">
            Issue-by-issue investigator plan using litigation-strength rankings and multi-stage
            dispute strategy. Advisory only — prepares letter drafts; never auto-files.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to={`/cases/${caseId}#dispute-strategy`}>
            <Button variant="secondary">Strategy panel</Button>
          </Link>
          <Link to={`/cases/${caseId}/accounts`}>
            <Button variant="secondary">Accounts</Button>
          </Link>
          <Link to={`/guides/dispute-workflow?case_id=${caseId}`}>
            <Button variant="secondary">Workflow guide</Button>
          </Link>
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <Card title="Strategy snapshot">
          {strategyQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : strategyQuery.isError ? (
            <p className="text-sm text-red-600">
              {strategyQuery.error instanceof ApiClientError && strategyQuery.error.status === 404
                ? 'Import and parse credit reports to generate a playbook.'
                : strategyQuery.error instanceof Error
                  ? strategyQuery.error.message
                  : 'Failed to load strategy'}
            </p>
          ) : strategyQuery.data ? (
            <div className="space-y-2">
              <div className="flex flex-wrap gap-2 text-xs">
                <Badge variant="default">
                  {strategyQuery.data.summary.accounts_planned} accounts
                </Badge>
                <Badge variant="default">{strategyQuery.data.summary.issues_covered} issues</Badge>
                <Badge variant="danger">
                  {strategyQuery.data.summary.high_strength_accounts} high-strength
                </Badge>
                <Badge variant="warning">{strategyQuery.data.summary.cfpb_recommended} CFPB</Badge>
                <Badge variant="info">
                  {strategyQuery.data.summary.attorney_recommended} attorney
                </Badge>
              </div>
              <p className="text-xs text-gray-500">{strategyQuery.data.disclaimer}</p>
            </div>
          ) : null}
        </Card>

        <Card title="Issue strength">
          {strengthQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : strengthQuery.data ? (
            <div className="flex flex-wrap gap-2 text-xs">
              <Badge variant="default">{strengthQuery.data.summary.issues_scored} scored</Badge>
              <Badge variant="danger">{strengthQuery.data.summary.high_priority} high</Badge>
              <Badge variant="warning">{strengthQuery.data.summary.medium_priority} medium</Badge>
              <Badge variant="info">{strengthQuery.data.summary.low_priority} low</Badge>
              <Badge variant="default">top {strengthQuery.data.summary.top_score}</Badge>
            </div>
          ) : (
            <p className="text-sm text-gray-500">No ranked issues yet.</p>
          )}
        </Card>

        <Card title="Clock & next actions">
          {summaryQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading…</p>
          ) : summaryQuery.data ? (
            <div className="space-y-2 text-sm text-gray-700">
              <p>
                {summaryQuery.data.disputed_accounts}/{summaryQuery.data.total_accounts} accounts
                disputed · {summaryQuery.data.total_responses} responses
              </p>
              {summaryQuery.data.next_deadline ? (
                <p className="text-xs text-gray-500">
                  Next deadline {new Date(summaryQuery.data.next_deadline).toLocaleString()}
                  {summaryQuery.data.next_deadline_creditor
                    ? ` · ${summaryQuery.data.next_deadline_creditor}`
                    : null}
                </p>
              ) : (
                <p className="text-xs text-gray-500">No open §611 deadline on file.</p>
              )}
              {summaryQuery.data.action_items.length > 0 ? (
                <ul className="space-y-1 text-xs">
                  {summaryQuery.data.action_items.slice(0, 4).map((item) => (
                    <li key={item.account_id}>
                      <Link
                        to={`/accounts/${item.account_id}`}
                        className="text-brand-600 hover:underline"
                      >
                        {item.creditor_name}
                      </Link>
                      {' · '}
                      {ACTION_LABELS[item.action]}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-gray-500">No redispute action items right now.</p>
              )}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No reinvestigation summary yet.</p>
          )}
        </Card>
      </div>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <label className="sr-only" htmlFor="playbook-filter">
          Filter accounts
        </label>
        <input
          id="playbook-filter"
          type="search"
          placeholder="Filter by creditor, bureau, rule…"
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          className="w-full max-w-md rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        <p className="text-xs text-gray-500">
          {strategies.length} account plan{strategies.length === 1 ? '' : 's'}
        </p>
      </div>

      {prepareMutation.isError ? (
        <p className="mb-4 text-sm text-red-600">
          {prepareMutation.error instanceof Error
            ? prepareMutation.error.message
            : 'Failed to prepare letter draft'}
        </p>
      ) : null}

      {prepareMutation.data ? (
        <div className="mb-4 rounded-md border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-700">
          Prepared {prepareMutation.data.prepared.length} letter draft(s) for{' '}
          {prepareMutation.data.stage_kind}.
          {prepareMutation.data.prepared[0]?.account_id ? (
            <>
              {' '}
              <Link
                to={`/accounts/${prepareMutation.data.prepared[0].account_id}`}
                className="text-brand-600 hover:underline"
              >
                Open account
              </Link>
            </>
          ) : null}
        </div>
      ) : null}

      {strategyQuery.isLoading ? (
        <p className="text-sm text-gray-500">Building account playbooks…</p>
      ) : null}

      {strategyQuery.data && strategies.length === 0 ? (
        <Card>
          <p className="text-sm text-gray-500">
            {filter
              ? 'No account plans match this filter.'
              : 'No dispute strategies yet. Import OCR’d credit reports and run findings first.'}
          </p>
        </Card>
      ) : null}

      <ul className="space-y-4">
        {strategies.map((strategy) => (
          <AccountPlaybookCard
            key={strategy.account_key}
            caseId={caseId}
            strategy={strategy}
            issues={strengthQuery.data?.issues ?? []}
            pendingPrepareKey={pendingPrepareKey}
            onPrepare={(stageKind, accountKey) =>
              prepareMutation.mutate({ stage_kind: stageKind, account_key: accountKey })
            }
          />
        ))}
      </ul>

      {strengthQuery.data && strengthQuery.data.issues.length > 0 ? (
        <Card className="mt-8" title="Full issue priority queue">
          <p className="mb-3 text-sm text-gray-500">
            All ranked issues for this case (strongest first). Linked into account cards above when
            match keys align.
          </p>
          <ol className="space-y-2">
            {strengthQuery.data.issues.map((issue) => (
              <li
                key={issue.source_id}
                className="flex flex-wrap items-start justify-between gap-2 rounded-md border border-gray-100 px-3 py-2"
              >
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    #{issue.rank} · {issue.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {issue.creditor_name ?? 'Unknown'}
                    {issue.bureau ? ` · ${issue.bureau}` : ''} · {issue.source_kind}
                  </p>
                  <Link
                    to={caseFindingDeepLink(caseId, issue.source_kind, issue.source_id)}
                    className="mt-1 inline-block text-xs text-brand-600 hover:underline"
                  >
                    View finding on case
                  </Link>
                </div>
                <Badge variant={scoreVariant(issue.score)}>{issue.score}/100</Badge>
              </li>
            ))}
          </ol>
        </Card>
      ) : null}
    </div>
  );
}
