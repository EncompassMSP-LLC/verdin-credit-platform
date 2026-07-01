import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ApiClientError,
  compareDocumentParsedCreditReport,
  getDocumentDuplicateGroup,
  listDocuments,
} from '@verdin/api-client';
import { Card } from '@verdin/ui';
import { Link } from 'react-router-dom';
import { DocumentDuplicateAlert } from '../documents/DocumentDuplicatePanel';
import {
  ParsedReportComparisonPanel,
  type ParsedReportTradelineHighlight,
} from './ParsedReportComparisonPanel';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

export function CreditReportHistoryPanel({
  caseId,
  highlightTradeline,
  title = 'Credit report history',
  className,
}: {
  caseId: string;
  highlightTradeline?: ParsedReportTradelineHighlight;
  title?: string;
  className?: string;
}) {
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);

  const documentsQuery = useQuery({
    queryKey: ['case-credit-reports', caseId],
    queryFn: () =>
      listDocuments({
        case_id: caseId,
        page_size: 50,
        sort_by: 'created_at',
        sort_order: 'desc',
      }),
  });

  const creditReports = useMemo(
    () =>
      documentsQuery.data?.items.filter((document) => document.document_type === 'credit_report') ??
      [],
    [documentsQuery.data?.items],
  );

  const activeDocumentId = useMemo(() => {
    if (creditReports.length === 0) {
      return null;
    }
    if (
      selectedDocumentId &&
      creditReports.some((document) => document.id === selectedDocumentId)
    ) {
      return selectedDocumentId;
    }
    return creditReports[0].id;
  }, [creditReports, selectedDocumentId]);

  const selectedDocument = creditReports.find((document) => document.id === activeDocumentId);

  const comparisonQuery = useQuery({
    queryKey: ['document-parsed-credit-report-comparison', activeDocumentId],
    queryFn: () => compareDocumentParsedCreditReport(activeDocumentId!),
    enabled: Boolean(activeDocumentId),
    retry: false,
  });

  const duplicateGroupQuery = useQuery({
    queryKey: ['document-duplicates', activeDocumentId],
    queryFn: () => getDocumentDuplicateGroup(activeDocumentId!),
    enabled: Boolean(activeDocumentId) && Boolean(selectedDocument),
    retry: false,
  });

  return (
    <Card title={title} className={className}>
      {documentsQuery.isLoading ? (
        <p className="text-sm text-gray-500">Loading credit reports...</p>
      ) : documentsQuery.isError ? (
        <p className="text-sm text-red-600">
          {documentsQuery.error instanceof Error
            ? documentsQuery.error.message
            : 'Failed to load credit reports'}
        </p>
      ) : creditReports.length === 0 ? (
        <p className="text-sm text-gray-500">
          No classified credit reports are linked to this case yet.
        </p>
      ) : (
        <div className="space-y-4">
          <div>
            <label
              htmlFor={`credit-report-select-${caseId}`}
              className="block text-sm font-medium text-gray-700"
            >
              Compare report
            </label>
            <select
              id={`credit-report-select-${caseId}`}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 sm:max-w-xl"
              value={activeDocumentId ?? ''}
              onChange={(event) => setSelectedDocumentId(event.target.value)}
            >
              {creditReports.map((document) => (
                <option key={document.id} value={document.id}>
                  {document.title} ({formatDateTime(document.created_at)})
                  {document.is_duplicate ? ' · duplicate' : ''}
                </option>
              ))}
            </select>
            {selectedDocument ? (
              <p className="mt-2 text-xs text-gray-500">
                <Link
                  to={`/documents/${selectedDocument.id}`}
                  className="text-brand-600 hover:underline"
                >
                  Open {selectedDocument.file_name}
                </Link>
              </p>
            ) : null}
          </div>

          {selectedDocument && duplicateGroupQuery.data ? (
            <DocumentDuplicateAlert
              currentDocument={selectedDocument}
              duplicateGroup={duplicateGroupQuery.data}
            />
          ) : null}

          {comparisonQuery.isLoading ? (
            <p className="text-sm text-gray-500">Loading historical comparison...</p>
          ) : comparisonQuery.isError ? (
            <p className="text-sm text-gray-500">
              {comparisonQuery.error instanceof ApiClientError &&
              comparisonQuery.error.status === 404
                ? 'Structured parser output is not available for the selected report yet.'
                : comparisonQuery.error instanceof Error
                  ? comparisonQuery.error.message
                  : 'Failed to load comparison'}
            </p>
          ) : (
            <ParsedReportComparisonPanel
              comparison={comparisonQuery.data}
              highlightTradeline={highlightTradeline}
              documentLink={activeDocumentId ? `/documents/${activeDocumentId}` : undefined}
              previousDocumentLink={
                comparisonQuery.data?.previous_document_id
                  ? `/documents/${comparisonQuery.data.previous_document_id}`
                  : null
              }
            />
          )}
        </div>
      )}
    </Card>
  );
}
