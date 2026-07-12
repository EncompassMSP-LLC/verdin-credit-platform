import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  getCaseComplianceEvidenceLinks,
  type ComplianceEvidenceLinkItem,
  type ComplianceEvidenceSummary,
} from '@verdin/api-client';
import { Badge, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function SummaryBadges({ summary }: { summary: ComplianceEvidenceSummary }) {
  return (
    <div className="flex flex-wrap gap-2 text-xs">
      <Badge variant="default">{summary.findings_linked} findings</Badge>
      <Badge variant="info">{summary.report_links} report links</Badge>
      <Badge variant="warning">{summary.exhibits_available} exhibits</Badge>
      <Badge variant="default">{summary.with_pages} with pages</Badge>
    </div>
  );
}

function EvidenceItem({ item }: { item: ComplianceEvidenceLinkItem }) {
  return (
    <li className="rounded-md border border-gray-200 px-4 py-3">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="text-sm font-medium text-gray-900">{item.title}</p>
          <p className="mt-1 text-xs text-gray-500">
            {item.source_kind} · {item.rule_id}
            {item.bureau ? ` · ${item.bureau}` : ''}
          </p>
        </div>
        <Badge
          variant={
            item.severity === 'high' ? 'danger' : item.severity === 'medium' ? 'warning' : 'info'
          }
        >
          {item.severity}
        </Badge>
      </div>

      <p className="mt-2 text-sm text-gray-600">
        {item.creditor_name ?? 'Unknown creditor'}
        {item.account_number_masked ? ` · ${item.account_number_masked}` : ''}
      </p>

      <div className="mt-3 space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Report evidence</p>
        <ul className="space-y-1">
          {item.report_links.map((link) => (
            <li key={link.document_id} className="text-sm text-gray-700">
              <Link
                to={`/documents/${link.document_id}`}
                className="text-brand-600 hover:underline"
              >
                Open {link.bureau ?? 'report'} document
              </Link>
              <span className="text-xs text-gray-500">
                {' '}
                · pages {link.page_confidence}
                {link.page_numbers && link.page_numbers.length > 0
                  ? ` (${link.page_numbers.join(', ')})`
                  : ''}
                {link.excerpt_available ? ' · excerpt available' : ''}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {item.exhibit_links.length > 0 ? (
        <div className="mt-3 space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Exhibits</p>
          <ul className="space-y-1">
            {item.exhibit_links.map((exhibit) => (
              <li key={`${exhibit.document_id}-${exhibit.role}`} className="text-sm text-gray-700">
                <Link
                  to={`/documents/${exhibit.document_id}`}
                  className="text-brand-600 hover:underline"
                >
                  {exhibit.label}
                </Link>
                <span className="text-xs text-gray-500">
                  {' '}
                  · {exhibit.role} · {exhibit.document_type}
                </span>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      {item.checklist_hints.length > 0 ? (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-xs text-gray-500">
          {item.checklist_hints.map((hint) => (
            <li key={hint}>{hint}</li>
          ))}
        </ul>
      ) : null}
    </li>
  );
}

export function CaseComplianceEvidencePanel({
  caseId,
  className,
  id,
}: {
  caseId: string;
  className?: string;
  id?: string;
}) {
  const evidenceQuery = useQuery({
    queryKey: ['case-compliance-evidence-links', caseId],
    queryFn: () => getCaseComplianceEvidenceLinks(caseId),
    retry: false,
  });

  return (
    <div id={id} className={className}>
      <Card title="Compliance evidence links">
        <p className="text-sm text-gray-500">
          Links Metro 2 and FCRA findings to source bureau reports, case exhibits, and investigator
          checklist hints. Exact PDF page maps remain best-effort / deferred.
        </p>

        {evidenceQuery.isLoading ? (
          <p className="mt-3 text-sm text-gray-500">Loading evidence links…</p>
        ) : null}

        {evidenceQuery.isError ? (
          <p className="mt-3 text-sm text-red-600">
            {evidenceQuery.error instanceof ApiClientError && evidenceQuery.error.status === 404
              ? 'No parsed credit reports are available for this case yet.'
              : evidenceQuery.error instanceof Error
                ? evidenceQuery.error.message
                : 'Failed to load evidence links'}
          </p>
        ) : null}

        {evidenceQuery.data ? (
          <div className="mt-4 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm text-gray-600">
                {evidenceQuery.data.summary.findings_linked} findings linked
              </p>
              <SummaryBadges summary={evidenceQuery.data.summary} />
            </div>

            {evidenceQuery.data.items.length === 0 ? (
              <p className="text-sm text-gray-500">
                No Metro 2 or FCRA findings to attach evidence to yet.
              </p>
            ) : (
              <ul className="space-y-3">
                {evidenceQuery.data.items.map((item) => (
                  <EvidenceItem key={item.source_id} item={item} />
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </Card>
    </div>
  );
}
