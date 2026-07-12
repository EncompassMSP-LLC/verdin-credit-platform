import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseMetro2Findings,
  getDocumentMetro2Findings,
  type Metro2Finding,
  type Metro2FindingSummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function severityVariant(
  severity: Metro2Finding['severity'],
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

function SummaryBadges({ summary }: { summary: Metro2FindingSummary }) {
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
  emptyMessage,
}: {
  findings: Metro2Finding[];
  emptyMessage: string;
}) {
  if (findings.length === 0) {
    return <p className="mt-3 text-sm text-gray-500">{emptyMessage}</p>;
  }

  return (
    <ul className="mt-4 space-y-3">
      {findings.map((finding) => (
        <li
          key={`${finding.rule_id}-${finding.tradeline_index}-${finding.creditor_name ?? ''}`}
          className="rounded-md border border-gray-200 px-4 py-3"
        >
          <div className="flex flex-wrap items-start justify-between gap-2">
            <div>
              <p className="text-sm font-medium text-gray-900">{finding.title}</p>
              <p className="mt-1 text-xs text-gray-500">{finding.rule_id}</p>
            </div>
            <Badge variant={severityVariant(finding.severity)}>{finding.severity}</Badge>
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
      ))}
    </ul>
  );
}

export function DocumentMetro2FindingsPanel({
  documentId,
  className,
}: {
  documentId: string;
  className?: string;
}) {
  const findingsQuery = useQuery({
    queryKey: ['document-metro2-findings', documentId],
    queryFn: () => getDocumentMetro2Findings(documentId),
    retry: false,
  });

  return (
    <div className={`rounded-md border border-gray-200 p-4 ${className ?? ''}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Metro 2 consistency findings</h4>
          <p className="mt-1 text-sm text-gray-500">
            Deterministic field checks for investigator review. Not a full CDIA Metro 2 audit.
          </p>
        </div>
        {findingsQuery.data ? <SummaryBadges summary={findingsQuery.data.summary} /> : null}
      </div>

      {findingsQuery.isLoading ? (
        <p className="mt-3 text-sm text-gray-500">Loading Metro 2 findings…</p>
      ) : null}

      {findingsQuery.isError ? (
        <p className="mt-3 text-sm text-red-600">
          {findingsQuery.error instanceof ApiClientError && findingsQuery.error.status === 404
            ? 'Parsed credit report is not available yet.'
            : findingsQuery.error instanceof Error
              ? findingsQuery.error.message
              : 'Failed to load Metro 2 findings'}
        </p>
      ) : null}

      {findingsQuery.data ? (
        <FindingsList
          findings={findingsQuery.data.findings}
          emptyMessage="No Metro 2 consistency issues were flagged on this report."
        />
      ) : null}
    </div>
  );
}

export function CaseMetro2FindingsPanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const findingsQuery = useQuery({
    queryKey: ['case-metro2-findings', caseId],
    queryFn: () => getCaseMetro2Findings(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Metro 2 consistency findings">
        <p className="text-sm text-gray-500">
          Aggregate deterministic checks across the latest parsed report for each bureau on this
          case.
        </p>

        {findingsQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading Metro 2 findings…</p>
        ) : null}

        {findingsQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {findingsQuery.error instanceof ApiClientError && findingsQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : findingsQuery.error instanceof Error
                ? findingsQuery.error.message
                : 'Failed to load Metro 2 findings'}
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
                  emptyMessage="No findings for this bureau report."
                />
              </div>
            ))}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
