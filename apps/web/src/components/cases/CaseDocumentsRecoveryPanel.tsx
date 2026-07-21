import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  bulkReclassifyCaseDocuments,
  bulkReextractCaseMetadata,
  bulkReparseCaseCreditReports,
  bulkRetryCaseOcr,
  listDocuments,
} from '@verdin/api-client';
import { Button, Card } from '@verdin/ui';
import { Link } from 'react-router-dom';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function formatDocType(value: string | null | undefined) {
  if (!value) return 'unclassified';
  return value.replaceAll('_', ' ');
}

export function CaseDocumentsRecoveryPanel({
  caseId,
  title = 'Document pipeline recovery',
  className,
}: {
  caseId: string;
  title?: string;
  className?: string;
}) {
  const queryClient = useQueryClient();
  const [bulkSummary, setBulkSummary] = useState<string | null>(null);

  const documentsQuery = useQuery({
    queryKey: ['case-documents-recovery', caseId],
    queryFn: () =>
      listDocuments({
        case_id: caseId,
        page_size: 50,
        sort_by: 'created_at',
        sort_order: 'desc',
      }),
  });

  const documents = documentsQuery.data?.items ?? [];
  const failedOcrCount = useMemo(
    () => documents.filter((document) => document.processing_status === 'failed').length,
    [documents],
  );
  const unclassifiedCount = useMemo(
    () => documents.filter((document) => !document.document_type).length,
    [documents],
  );
  const creditReportCount = useMemo(
    () => documents.filter((document) => document.document_type === 'credit_report').length,
    [documents],
  );

  const invalidateCaseDocuments = () => {
    queryClient.invalidateQueries({ queryKey: ['case-documents-recovery', caseId] });
    queryClient.invalidateQueries({ queryKey: ['case-credit-reports', caseId] });
    queryClient.invalidateQueries({ queryKey: ['documents'] });
  };

  const bulkReextractMutation = useMutation({
    mutationFn: () => bulkReextractCaseMetadata(caseId),
    onSuccess: (result) => {
      setBulkSummary(
        `Queued ${result.queued_count} metadata re-extract job(s); skipped ${result.skipped_count}.`,
      );
      invalidateCaseDocuments();
    },
    onError: (error) => {
      setBulkSummary(
        error instanceof Error ? error.message : 'Failed to enqueue bulk metadata re-extract',
      );
    },
  });

  const bulkReclassifyMutation = useMutation({
    mutationFn: () => bulkReclassifyCaseDocuments(caseId),
    onSuccess: (result) => {
      setBulkSummary(
        `Queued ${result.queued_count} re-classify job(s); skipped ${result.skipped_count}.`,
      );
      invalidateCaseDocuments();
    },
    onError: (error) => {
      setBulkSummary(error instanceof Error ? error.message : 'Failed to enqueue bulk re-classify');
    },
  });

  const bulkOcrRetryMutation = useMutation({
    mutationFn: () => bulkRetryCaseOcr(caseId),
    onSuccess: (result) => {
      setBulkSummary(
        `Queued ${result.queued_count} OCR retry job(s); skipped ${result.skipped_count}.`,
      );
      invalidateCaseDocuments();
    },
    onError: (error) => {
      setBulkSummary(error instanceof Error ? error.message : 'Failed to enqueue bulk OCR retry');
    },
  });

  const bulkReparseMutation = useMutation({
    mutationFn: () => bulkReparseCaseCreditReports(caseId),
    onSuccess: (result) => {
      setBulkSummary(
        `Queued ${result.queued_count} re-parse job(s); skipped ${result.skipped_count}.`,
      );
      invalidateCaseDocuments();
    },
    onError: (error) => {
      setBulkSummary(
        error instanceof Error ? error.message : 'Failed to enqueue bulk credit report re-parse',
      );
    },
  });

  const bulkActionsPending =
    bulkReparseMutation.isPending ||
    bulkReextractMutation.isPending ||
    bulkReclassifyMutation.isPending ||
    bulkOcrRetryMutation.isPending;

  return (
    <Card title={title} className={className}>
      {documentsQuery.isLoading ? (
        <p className="text-sm text-gray-500">Loading case documents...</p>
      ) : documentsQuery.isError ? (
        <p className="text-sm text-red-600">
          {documentsQuery.error instanceof Error
            ? documentsQuery.error.message
            : 'Failed to load case documents'}
        </p>
      ) : documents.length === 0 ? (
        <p className="text-sm text-gray-500">No documents are linked to this case yet.</p>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            {documents.length} document{documents.length === 1 ? '' : 's'}
            {failedOcrCount > 0 ? ` · ${failedOcrCount} failed OCR` : ''}
            {unclassifiedCount > 0 ? ` · ${unclassifiedCount} unclassified` : ''}
            {creditReportCount > 0 ? ` · ${creditReportCount} credit report` : ''}
          </p>

          <div className="flex flex-col gap-2 sm:max-w-md">
            <Button
              variant="secondary"
              onClick={() => bulkOcrRetryMutation.mutate()}
              disabled={bulkActionsPending}
            >
              {bulkOcrRetryMutation.isPending ? 'Retrying OCR…' : 'Retry failed OCR (case)'}
            </Button>
            <Button
              variant="secondary"
              onClick={() => bulkReclassifyMutation.mutate()}
              disabled={bulkActionsPending}
            >
              {bulkReclassifyMutation.isPending
                ? 'Re-classifying…'
                : 'Re-classify documents (case)'}
            </Button>
            <Button
              variant="secondary"
              onClick={() => bulkReextractMutation.mutate()}
              disabled={bulkActionsPending}
            >
              {bulkReextractMutation.isPending ? 'Re-extracting…' : 'Re-extract metadata (case)'}
            </Button>
            <Button
              variant="secondary"
              onClick={() => bulkReparseMutation.mutate()}
              disabled={bulkActionsPending}
            >
              {bulkReparseMutation.isPending ? 'Re-parsing…' : 'Re-parse all credit reports'}
            </Button>
          </div>

          {bulkSummary ? <p className="text-sm text-gray-600">{bulkSummary}</p> : null}

          <ul className="divide-y divide-gray-100 rounded-md border border-gray-200">
            {documents.slice(0, 10).map((document) => (
              <li key={document.id} className="flex items-start justify-between gap-3 px-3 py-2">
                <div className="min-w-0">
                  <Link
                    to={`/documents/${document.id}`}
                    className="text-sm font-medium text-brand-600 hover:underline"
                  >
                    {document.title}
                  </Link>
                  <p className="truncate text-xs text-gray-500">
                    {document.file_name} · {formatDocType(document.document_type)} ·{' '}
                    {document.processing_status} · {formatDateTime(document.created_at)}
                  </p>
                </div>
              </li>
            ))}
          </ul>
          {documents.length > 10 ? (
            <p className="text-xs text-gray-500">Showing 10 of {documents.length} documents.</p>
          ) : null}
        </div>
      )}
    </Card>
  );
}
