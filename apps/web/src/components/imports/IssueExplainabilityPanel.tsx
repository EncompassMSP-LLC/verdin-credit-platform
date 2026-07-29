import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  createCaseLetterDraft,
  getCaseIssueExplainability,
  type FindingStrengthBand,
  type ImpactCategory,
  type IssueExplainabilityCard,
  type IssueExplainabilitySummary,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { useState } from 'react';

function strengthVariant(band: FindingStrengthBand): 'danger' | 'warning' | 'info' | 'default' {
  if (band === 'strong') return 'danger';
  if (band === 'moderate') return 'warning';
  if (band === 'needs_more_evidence') return 'info';
  return 'default';
}

function impactLabel(impact: ImpactCategory): string {
  if (impact === 'no_score_impact_expected') return 'No score impact expected';
  return impact.replace(/_/g, ' ');
}

function SummaryBadges({ summary }: { summary: IssueExplainabilitySummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.issues_explained} explained</Badge>
      <Badge variant="danger">{summary.strong} strong</Badge>
      <Badge variant="warning">{summary.moderate} moderate</Badge>
      <Badge variant="info">{summary.needs_more_evidence} need evidence</Badge>
      <Badge variant="default">{summary.informational} informational</Badge>
      <Badge variant="danger">{summary.high_credit_impact} high credit impact</Badge>
      <Badge variant="warning">{summary.high_mortgage_impact} high mortgage impact</Badge>
    </div>
  );
}

function ExplainabilityCardRow({
  caseId,
  card,
}: {
  caseId: string;
  card: IssueExplainabilityCard;
}) {
  const queryClient = useQueryClient();
  const [message, setMessage] = useState<string | null>(null);
  const generateMutation = useMutation({
    mutationFn: () =>
      createCaseLetterDraft(caseId, {
        template_kind: 'bureau_dispute',
        issue_source_id: card.source_id,
      }),
    onSuccess: (draft) => {
      setMessage(`Draft created (${draft.workflow_status.replace(/_/g, ' ')}) — not sent.`);
      void queryClient.invalidateQueries({ queryKey: ['case-letter-drafts', caseId] });
      const el = document.getElementById('letter-draft-builder');
      el?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    },
    onError: (err: Error) => setMessage(err.message),
  });

  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">{card.title}</p>
          <p className="mt-1 text-xs text-gray-500">
            {card.source_kind} · {card.rule_id}
            {card.bureau ? ` · ${card.bureau}` : ''}
          </p>
        </div>
        <div className="flex flex-wrap gap-1">
          <Badge variant={strengthVariant(card.finding_strength)}>
            {card.finding_strength.replace(/_/g, ' ')}
          </Badge>
          <Badge variant="default">credit: {impactLabel(card.credit_profile_impact)}</Badge>
          <Badge variant="default">mortgage: {impactLabel(card.mortgage_readiness_impact)}</Badge>
        </div>
      </div>

      {(card.creditor_name || card.account_number_masked) && (
        <p className="mt-2 text-sm text-gray-700">
          {card.creditor_name ?? 'Account'}
          {card.account_number_masked ? ` · ${card.account_number_masked}` : ''}
        </p>
      )}

      <div className="mt-3 space-y-2 text-sm text-gray-700">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            What we found
          </p>
          <p className="mt-0.5">{card.what_we_found}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            Why this may be disputable
          </p>
          <p className="mt-0.5">{card.why_disputable}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            What could happen if corrected
          </p>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-gray-700">
            {card.possible_outcomes.map((outcome) => (
              <li key={outcome}>{outcome}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-gray-500">
            What would strengthen this case
          </p>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-gray-700">
            {card.evidence_recommendations.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <p className="text-xs text-gray-500">
          Recommended next action: {card.recommended_next_action}
        </p>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <Button
          type="button"
          size="sm"
          variant="secondary"
          onClick={() => {
            setMessage(null);
            generateMutation.mutate();
          }}
          loading={generateMutation.isPending}
          disabled={generateMutation.isPending}
        >
          Generate letter draft
        </Button>
        {message ? <p className="text-xs text-gray-600">{message}</p> : null}
      </div>
    </li>
  );
}

export function CaseIssueExplainabilityPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const explainQuery = useQuery({
    queryKey: ['case-issue-explainability', caseId],
    queryFn: () => getCaseIssueExplainability(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Issue explanation cards">
        <p className="text-sm text-gray-500">
          Plain-language explanations of detected issues with impact categories and evidence
          recommendations. Advisory only — never estimates score-point changes. Generate letter
          creates a staff-gated draft only (never auto-sent).
        </p>

        {explainQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading issue explanations…</p>
        ) : null}

        {explainQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {explainQuery.error instanceof ApiClientError && explainQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : explainQuery.error instanceof Error
                ? explainQuery.error.message
                : 'Failed to load issue explanations'}
          </p>
        ) : null}

        {explainQuery.data ? (
          <div className="mt-3 space-y-3">
            <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-950">
              {explainQuery.data.disclaimer}
            </p>
            <SummaryBadges summary={explainQuery.data.summary} />
            {explainQuery.data.cards.length === 0 ? (
              <p className="text-sm text-gray-500">No issues to explain yet.</p>
            ) : (
              <ul className="space-y-3">
                {explainQuery.data.cards.map((card) => (
                  <ExplainabilityCardRow key={card.source_id} caseId={caseId} card={card} />
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
