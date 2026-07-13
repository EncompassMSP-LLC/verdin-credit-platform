import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  downloadCaseAttorneyChecklist,
  downloadCaseAttorneyChecklistPacket,
  downloadCaseCfpbChecklist,
  downloadCaseCfpbChecklistPacket,
  getCaseAttorneyChecklist,
  getCaseCfpbChecklist,
  getCaseDisputeStrategy,
  prepareCaseDisputeStrategyStage,
  upsertCaseChecklistOverride,
  type AccountAttorneyChecklist,
  type AccountCfpbChecklist,
  type AccountDisputeStrategy,
  type DisputeStrategyStage,
  type DisputeStrategyStageKind,
  type DisputeStrategySummary,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useState } from 'react';
import { Link } from 'react-router-dom';

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

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

function completionBadge(status: string | undefined, source?: string) {
  const label = status === 'present' ? 'present' : status === 'missing' ? 'missing' : 'unknown';
  const variant = status === 'present' ? 'success' : status === 'missing' ? 'warning' : 'default';
  return (
    <Badge variant={variant}>
      {label}
      {source === 'staff' ? ' · staff' : ''}
    </Badge>
  );
}

function ChecklistAccount({
  account,
  accent,
  checklistKind,
  onToggle,
  pendingKey,
}: {
  account: AccountCfpbChecklist | AccountAttorneyChecklist;
  accent: 'amber' | 'slate';
  checklistKind: 'cfpb' | 'attorney';
  onToggle: (
    accountKey: string,
    itemId: string,
    markPresent: boolean,
    note?: string | null,
  ) => void;
  pendingKey: string | null;
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
        {account.items.map((item) => {
          const key = `${checklistKind}:${account.account_key}:${item.item_id}`;
          const isStaff = item.completion_source === 'staff';
          return (
            <li key={item.item_id} className="text-xs text-gray-700">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">
                  {item.required ? 'Required' : 'Optional'} · {item.category}:
                </span>{' '}
                {item.title}
                {completionBadge(item.completion_status, item.completion_source)}
                <Button
                  size="sm"
                  variant="secondary"
                  loading={pendingKey === key}
                  onClick={() => {
                    if (isStaff) {
                      onToggle(account.account_key, item.item_id, false);
                      return;
                    }
                    const note = window.prompt(
                      'Optional staff note for this override (leave blank to skip):',
                      '',
                    );
                    if (note === null) {
                      return;
                    }
                    onToggle(
                      account.account_key,
                      item.item_id,
                      true,
                      note.trim() ? note.trim() : null,
                    );
                  }}
                >
                  {isStaff ? 'Clear override' : 'Mark complete'}
                </Button>
              </div>
              <span className="block text-gray-500">{item.detail}</span>
              {isStaff && item.override_note ? (
                <span className="mt-0.5 block text-gray-500 italic">
                  Staff note: {item.override_note}
                </span>
              ) : null}
            </li>
          );
        })}
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
  const [downloadingCfpb, setDownloadingCfpb] = useState(false);
  const [downloadingAttorney, setDownloadingAttorney] = useState(false);
  const [downloadingCfpbPacket, setDownloadingCfpbPacket] = useState(false);
  const [downloadingAttorneyPacket, setDownloadingAttorneyPacket] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);
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

  const overrideMutation = useMutation({
    mutationFn: (input: {
      checklist_kind: 'cfpb' | 'attorney';
      account_key: string;
      item_id: string;
      markPresent: boolean;
      note?: string | null;
    }) =>
      upsertCaseChecklistOverride(caseId, {
        checklist_kind: input.checklist_kind,
        account_key: input.account_key,
        item_id: input.item_id,
        completion_status: input.markPresent ? 'present' : null,
        note: input.markPresent ? (input.note ?? null) : null,
      }),
    onSuccess: (_data, variables) => {
      const key =
        variables.checklist_kind === 'cfpb'
          ? ['case-cfpb-checklist', caseId]
          : ['case-attorney-checklist', caseId];
      void queryClient.invalidateQueries({ queryKey: key });
    },
  });

  const pendingOverrideKey = overrideMutation.isPending
    ? `${overrideMutation.variables?.checklist_kind}:${overrideMutation.variables?.account_key}:${overrideMutation.variables?.item_id}`
    : null;

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
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900">CFPB escalation checklist</p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={downloadingCfpb}
                      onClick={() => {
                        setDownloadError(null);
                        setDownloadingCfpb(true);
                        void downloadCaseCfpbChecklist(caseId)
                          .then(({ blob, filename }) => downloadBlob(blob, filename))
                          .catch((error: unknown) => {
                            setDownloadError(
                              error instanceof Error
                                ? error.message
                                : 'Failed to download CFPB checklist',
                            );
                          })
                          .finally(() => setDownloadingCfpb(false));
                      }}
                    >
                      Download checklist (.md)
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={downloadingCfpbPacket}
                      onClick={() => {
                        setDownloadError(null);
                        setDownloadingCfpbPacket(true);
                        void downloadCaseCfpbChecklistPacket(caseId, { letter_format: 'pdf' })
                          .then(({ blob, filename }) => downloadBlob(blob, filename))
                          .catch((error: unknown) => {
                            setDownloadError(
                              error instanceof Error
                                ? error.message
                                : 'Failed to download CFPB packet',
                            );
                          })
                          .finally(() => setDownloadingCfpbPacket(false));
                      }}
                    >
                      Download packet (.zip)
                    </Button>
                  </div>
                </div>
                <p className="text-xs text-gray-500">{cfpbQuery.data.disclaimer}</p>
                <p className="text-xs text-gray-500">
                  {cfpbQuery.data.summary.accounts_listed} account(s) ·{' '}
                  {cfpbQuery.data.summary.required_items} required ·{' '}
                  {cfpbQuery.data.summary.optional_items} optional ·{' '}
                  {cfpbQuery.data.summary.items_present ?? 0} present ·{' '}
                  {cfpbQuery.data.summary.items_missing ?? 0} missing ·{' '}
                  {cfpbQuery.data.summary.items_unknown ?? 0} unknown
                </p>
                <ul className="space-y-2">
                  {cfpbQuery.data.accounts.map((account) => (
                    <ChecklistAccount
                      key={account.account_key}
                      account={account}
                      accent="amber"
                      checklistKind="cfpb"
                      pendingKey={pendingOverrideKey}
                      onToggle={(accountKey, itemId, markPresent, note) =>
                        overrideMutation.mutate({
                          checklist_kind: 'cfpb',
                          account_key: accountKey,
                          item_id: itemId,
                          markPresent,
                          note,
                        })
                      }
                    />
                  ))}
                </ul>
              </div>
            ) : null}

            {attorneyQuery.data && attorneyQuery.data.accounts.length > 0 ? (
              <div className="space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-sm font-medium text-gray-900">Attorney-preserve checklist</p>
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={downloadingAttorney}
                      onClick={() => {
                        setDownloadError(null);
                        setDownloadingAttorney(true);
                        void downloadCaseAttorneyChecklist(caseId)
                          .then(({ blob, filename }) => downloadBlob(blob, filename))
                          .catch((error: unknown) => {
                            setDownloadError(
                              error instanceof Error
                                ? error.message
                                : 'Failed to download attorney checklist',
                            );
                          })
                          .finally(() => setDownloadingAttorney(false));
                      }}
                    >
                      Download checklist (.md)
                    </Button>
                    <Button
                      size="sm"
                      variant="secondary"
                      loading={downloadingAttorneyPacket}
                      onClick={() => {
                        setDownloadError(null);
                        setDownloadingAttorneyPacket(true);
                        void downloadCaseAttorneyChecklistPacket(caseId, {
                          letter_format: 'pdf',
                        })
                          .then(({ blob, filename }) => downloadBlob(blob, filename))
                          .catch((error: unknown) => {
                            setDownloadError(
                              error instanceof Error
                                ? error.message
                                : 'Failed to download attorney packet',
                            );
                          })
                          .finally(() => setDownloadingAttorneyPacket(false));
                      }}
                    >
                      Download packet (.zip)
                    </Button>
                  </div>
                </div>
                <p className="text-xs text-gray-500">{attorneyQuery.data.disclaimer}</p>
                <p className="text-xs text-gray-500">
                  {attorneyQuery.data.summary.accounts_listed} account(s) ·{' '}
                  {attorneyQuery.data.summary.required_items} required ·{' '}
                  {attorneyQuery.data.summary.optional_items} optional ·{' '}
                  {attorneyQuery.data.summary.escalation_flagged} escalation-flagged ·{' '}
                  {attorneyQuery.data.summary.items_present ?? 0} present ·{' '}
                  {attorneyQuery.data.summary.items_missing ?? 0} missing ·{' '}
                  {attorneyQuery.data.summary.items_unknown ?? 0} unknown
                </p>
                <ul className="space-y-2">
                  {attorneyQuery.data.accounts.map((account) => (
                    <ChecklistAccount
                      key={account.account_key}
                      account={account}
                      accent="slate"
                      checklistKind="attorney"
                      pendingKey={pendingOverrideKey}
                      onToggle={(accountKey, itemId, markPresent, note) =>
                        overrideMutation.mutate({
                          checklist_kind: 'attorney',
                          account_key: accountKey,
                          item_id: itemId,
                          markPresent,
                          note,
                        })
                      }
                    />
                  ))}
                </ul>
              </div>
            ) : null}

            {downloadError ? <p className="text-sm text-red-600">{downloadError}</p> : null}

            {overrideMutation.isError ? (
              <p className="text-sm text-red-600">
                {overrideMutation.error instanceof Error
                  ? overrideMutation.error.message
                  : 'Failed to update checklist override'}
              </p>
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
