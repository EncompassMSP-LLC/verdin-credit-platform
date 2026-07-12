import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseLitigationStrength,
  type LitigationStrengthIssue,
  type LitigationStrengthSummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';

function SummaryBadges({ summary }: { summary: LitigationStrengthSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.issues_scored} scored</Badge>
      <Badge variant="danger">{summary.high_priority} high</Badge>
      <Badge variant="warning">{summary.medium_priority} medium</Badge>
      <Badge variant="info">{summary.low_priority} low</Badge>
      <Badge variant="default">top {summary.top_score}</Badge>
      <Badge variant="default">avg {summary.average_score}</Badge>
    </div>
  );
}

function IssueRow({ issue }: { issue: LitigationStrengthIssue }) {
  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">
            #{issue.rank} · {issue.title}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            {issue.source_kind} · {issue.rule_id}
            {issue.bureau ? ` · ${issue.bureau}` : ''}
          </p>
        </div>
        <div className="flex flex-wrap gap-1">
          <Badge variant={issue.score >= 85 ? 'danger' : issue.score >= 70 ? 'warning' : 'info'}>
            {issue.score}/100
          </Badge>
          <Badge variant="default">{issue.severity}</Badge>
        </div>
      </div>
      <p className="mt-2 text-sm text-gray-700">
        {issue.creditor_name ?? 'Unknown creditor'}
        {issue.account_number_masked ? ` · ${issue.account_number_masked}` : ''}
      </p>
      <p className="mt-2 text-xs text-gray-500">{issue.rationale}</p>
      {issue.factors.length > 0 ? (
        <p className="mt-1 text-xs text-gray-400">Factors: {issue.factors.join(', ')}</p>
      ) : null}
    </li>
  );
}

export function CaseLitigationStrengthPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const strengthQuery = useQuery({
    queryKey: ['case-litigation-strength', caseId],
    queryFn: () => getCaseLitigationStrength(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Litigation strength ranking">
        <p className="text-sm text-gray-500">
          Heuristic ranking of Metro 2, FCRA, cross-bureau, and chronology issues by investigative
          strength. Not legal advice.
        </p>

        {strengthQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading litigation strength scores…</p>
        ) : null}

        {strengthQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {strengthQuery.error instanceof ApiClientError && strengthQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : strengthQuery.error instanceof Error
                ? strengthQuery.error.message
                : 'Failed to load litigation strength scores'}
          </p>
        ) : null}

        {strengthQuery.data ? (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">Ranked strongest arguments first</p>
              <SummaryBadges summary={strengthQuery.data.summary} />
            </div>

            {strengthQuery.data.issues.length === 0 ? (
              <p className="text-sm text-gray-500">No scored compliance issues yet.</p>
            ) : (
              <ul className="space-y-3">
                {strengthQuery.data.issues.map((issue) => (
                  <IssueRow key={issue.source_id} issue={issue} />
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
