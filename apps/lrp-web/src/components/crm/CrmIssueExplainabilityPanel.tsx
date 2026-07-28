'use client';

import {
  ApiClientError,
  getCaseIssueExplainability,
  type FindingStrengthBand,
  type ImpactCategory,
  type IssueExplainabilityCard,
} from '@verdin/api-client';
import { useQuery } from '@tanstack/react-query';

import { useCrmAuth } from '@/lib/crm/auth';

function impactLabel(impact: ImpactCategory): string {
  if (impact === 'no_score_impact_expected') return 'No score impact expected';
  return impact.replace(/_/g, ' ');
}

function strengthLabel(band: FindingStrengthBand): string {
  return band.replace(/_/g, ' ');
}

function CardBlock({ card }: { card: IssueExplainabilityCard }) {
  return (
    <article className="rounded-md border border-navy-900/10 bg-slate-50 p-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <h3 className="text-sm font-semibold text-navy-900">{card.title}</h3>
        <p className="text-xs text-slate-500">
          {strengthLabel(card.finding_strength)} · credit {impactLabel(card.credit_profile_impact)}{' '}
          · mortgage {impactLabel(card.mortgage_readiness_impact)}
        </p>
      </div>
      {(card.creditor_name || card.account_number_masked) && (
        <p className="mt-1 text-xs text-slate-600">
          {card.creditor_name ?? 'Account'}
          {card.account_number_masked ? ` · ${card.account_number_masked}` : ''}
        </p>
      )}
      <dl className="mt-3 space-y-2 text-sm text-slate-700">
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            What we found
          </dt>
          <dd className="mt-0.5">{card.what_we_found}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Why this may be disputable
          </dt>
          <dd className="mt-0.5">{card.why_disputable}</dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            What could happen if corrected
          </dt>
          <dd>
            <ul className="mt-1 list-disc space-y-1 pl-5">
              {card.possible_outcomes.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </dd>
        </div>
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            What would strengthen this case
          </dt>
          <dd>
            <ul className="mt-1 list-disc space-y-1 pl-5">
              {card.evidence_recommendations.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </dd>
        </div>
      </dl>
      <p className="mt-2 text-xs text-slate-500">{card.recommended_next_action}</p>
    </article>
  );
}

type Props = {
  caseId: string | undefined;
};

export function CrmIssueExplainabilityPanel({ caseId }: Props) {
  const { isAuthenticated, authMode } = useCrmAuth();
  const query = useQuery({
    queryKey: ['crm', 'case-issue-explainability', caseId],
    enabled: isAuthenticated && authMode === 'platform' && Boolean(caseId),
    queryFn: () => getCaseIssueExplainability(caseId!),
    retry: false,
  });

  if (!caseId) {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Potential issues</h2>
        <p className="mt-2 text-sm text-slate-500">
          Link a case to view plain-language issue cards.
        </p>
      </div>
    );
  }

  if (authMode !== 'platform') {
    return (
      <div className="rounded-md border border-navy-900/10 bg-white p-4">
        <h2 className="text-sm font-semibold">Potential issues</h2>
        <p className="mt-2 text-sm text-slate-500">
          Issue explanations require platform authentication (demo mode unavailable).
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-md border border-navy-900/10 bg-white p-4">
      <h2 className="text-sm font-semibold">Potential issues</h2>
      <p className="mt-2 text-sm text-slate-500">
        Plain-language cards for detected findings. Impact categories only — no score-point
        promises. Evidence vault uploads ship in a follow-up slice.
      </p>

      {query.isLoading ? (
        <p className="mt-3 text-sm text-slate-500">Loading issue explanations…</p>
      ) : null}

      {query.isError ? (
        <p className="mt-3 text-sm text-red-700">
          {query.error instanceof ApiClientError && query.error.status === 404
            ? 'No parsed credit reports are available for this case yet.'
            : query.error instanceof Error
              ? query.error.message
              : 'Failed to load issue explanations'}
        </p>
      ) : null}

      {query.data ? (
        <div className="mt-3 space-y-3">
          <p className="rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-950">
            {query.data.disclaimer}
          </p>
          <p className="text-xs text-slate-500">
            {query.data.summary.issues_explained} explained · {query.data.summary.strong} strong ·{' '}
            {query.data.summary.high_credit_impact} high credit impact ·{' '}
            {query.data.summary.high_mortgage_impact} high mortgage impact
          </p>
          {query.data.cards.length === 0 ? (
            <p className="text-sm text-slate-500">No issues to explain yet.</p>
          ) : (
            <div className="space-y-3">
              {query.data.cards.map((card) => (
                <CardBlock key={card.source_id} card={card} />
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
