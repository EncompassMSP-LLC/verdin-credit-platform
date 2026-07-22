import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseFcraFindings,
  getDocumentFcraFindings,
  type FcraFinding,
  type FcraFindingSummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link, useSearchParams } from 'react-router-dom';
import { findingMatchesSource } from '../../lib/findingDeepLink';

function severityVariant(
  severity: FcraFinding['severity'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (severity === 'high') return 'danger';
  if (severity === 'medium') return 'warning';
  return 'info';
}

function formatObserved(observed: Record<string, unknown>): string {
  return Object.entries(observed)
    .map(([key, value]) => `${key}=${value === null || value === undefined ? '—' : String(value)}`)
    .join(' · ');
}

function SummaryBadges({ summary }: { summary: FcraFindingSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.tradelines_evaluated} tradelines</Badge>
      <Badge variant="danger">{summary.high} high</Badge>
      <Badge variant="warning">{summary.medium} medium</Badge>
      <Badge variant="info">{summary.low} low</Badge>
      <Badge variant="default">{summary.total} total</Badge>
    </div>
  );
}

function FindingsList({
  findings,
  documentId,
  emptyMessage,
  highlightSourceId,
  highlightKind,
}: {
  findings: FcraFinding[];
  documentId: string;
  emptyMessage: string;
  highlightSourceId?: string | null;
  highlightKind?: 'fcra';
}) {
  if (findings.length === 0) {
    return <p className="mt-3 text-sm text-gray-500">{emptyMessage}</p>;
  }

  return (
    <ul className="mt-4 space-y-3">
      {findings.map((finding) => {
        const highlighted =
          highlightKind && highlightSourceId
            ? findingMatchesSource(
                {
                  rule_id: finding.rule_id,
                  tradeline_index: finding.tradeline_index,
                  document_id: documentId,
                },
                highlightSourceId,
                highlightKind,
              )
            : false;
        return (
          <li
            key={`${finding.rule_id}-${finding.tradeline_index}-${finding.creditor_name ?? ''}`}
            className={`rounded-md border px-4 py-3 ${
              highlighted
                ? 'border-brand-400 bg-brand-50/60 ring-2 ring-brand-200'
                : 'border-gray-200'
            }`}
          >
            <div className="flex flex-wrap items-start justify-between gap-2">
              <div>
                <p className="text-sm font-medium text-gray-900">{finding.title}</p>
                <p className="mt-1 text-xs text-gray-500">{finding.rule_id}</p>
              </div>
              <div className="flex flex-wrap gap-1">
                {highlighted ? <Badge variant="success">from playbook</Badge> : null}
                {finding.fcra_sections.map((section) => (
                  <Badge key={section} variant="info">
                    §{section}
                  </Badge>
                ))}
                <Badge variant={severityVariant(finding.severity)}>{finding.severity}</Badge>
              </div>
            </div>
            <p className="mt-2 text-sm text-gray-700">{finding.description}</p>
            <p className="mt-2 text-sm text-gray-600">
              {finding.creditor_name ?? 'Unknown creditor'}
              {finding.account_number_masked ? ` · ${finding.account_number_masked}` : ''}
              {` · tradeline #${finding.tradeline_index + 1}`}
            </p>
            <p className="mt-1 text-xs text-gray-500">
              Fields: {finding.fields.join(', ')}
              {Object.keys(finding.observed).length > 0
                ? ` · ${formatObserved(finding.observed)}`
                : null}
            </p>
          </li>
        );
      })}
    </ul>
  );
}

export function DocumentFcraFindingsPanel({
  documentId,
  className,
}: {
  documentId: string;
  className?: string;
}) {
  const findingsQuery = useQuery({
    queryKey: ['document-fcra-findings', documentId],
    queryFn: () => getDocumentFcraFindings(documentId),
    retry: false,
  });

  return (
    <div className={`rounded-md border border-gray-200 p-4 ${className ?? ''}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">FCRA checklist findings</h4>
          <p className="mt-1 text-sm text-gray-500">
            Deterministic statutory-oriented checks for investigator review. Not legal advice.
          </p>
          {findingsQuery.data?.as_of_date ? (
            <p className="mt-1 text-xs text-gray-500">As-of: {findingsQuery.data.as_of_date}</p>
          ) : null}
        </div>
        {findingsQuery.data ? <SummaryBadges summary={findingsQuery.data.summary} /> : null}
      </div>

      {findingsQuery.isLoading ? (
        <p className="mt-3 text-sm text-gray-500">Loading FCRA findings…</p>
      ) : null}

      {findingsQuery.isError ? (
        <p className="mt-3 text-sm text-red-600">
          {findingsQuery.error instanceof ApiClientError && findingsQuery.error.status === 404
            ? 'Parsed credit report is not available yet.'
            : findingsQuery.error instanceof Error
              ? findingsQuery.error.message
              : 'Failed to load FCRA findings'}
        </p>
      ) : null}

      {findingsQuery.data ? (
        <FindingsList
          findings={findingsQuery.data.findings}
          documentId={documentId}
          emptyMessage="No FCRA checklist issues were flagged on this report."
        />
      ) : null}
    </div>
  );
}

export function CaseFcraFindingsPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const [searchParams] = useSearchParams();
  const highlightSourceId = searchParams.get('finding_source');
  const findingsQuery = useQuery({
    queryKey: ['case-fcra-findings', caseId],
    queryFn: () => getCaseFcraFindings(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="FCRA checklist findings">
        <p className="text-sm text-gray-500">
          Aggregate deterministic statutory checks across the latest parsed report for each bureau
          on this case.
        </p>

        {findingsQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading FCRA findings…</p>
        ) : null}

        {findingsQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {findingsQuery.error instanceof ApiClientError && findingsQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : findingsQuery.error instanceof Error
                ? findingsQuery.error.message
                : 'Failed to load FCRA findings'}
          </p>
        ) : null}

        {findingsQuery.data ? (
          <div className="mt-4 space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">
                Reports evaluated:{' '}
                {findingsQuery.data.reports_evaluated.length > 0
                  ? findingsQuery.data.reports_evaluated.join(', ')
                  : 'none'}
              </p>
              <SummaryBadges summary={findingsQuery.data.summary} />
            </div>

            {findingsQuery.data.documents.map((documentFindings) => (
              <div
                key={documentFindings.document_id}
                className="rounded-md border border-gray-200 p-4"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="text-sm font-medium capitalize text-gray-900">
                      {documentFindings.bureau}
                    </h4>
                    {documentFindings.as_of_date ? (
                      <p className="mt-1 text-xs text-gray-500">
                        As-of: {documentFindings.as_of_date}
                      </p>
                    ) : null}
                    <Link
                      to={`/documents/${documentFindings.document_id}`}
                      className="mt-1 inline-block text-xs text-brand-600 hover:underline"
                    >
                      Open report document
                    </Link>
                  </div>
                  <SummaryBadges summary={documentFindings.summary} />
                </div>
                <FindingsList
                  findings={documentFindings.findings}
                  documentId={documentFindings.document_id}
                  emptyMessage="No findings for this bureau report."
                  highlightSourceId={highlightSourceId}
                  highlightKind="fcra"
                />
              </div>
            ))}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
