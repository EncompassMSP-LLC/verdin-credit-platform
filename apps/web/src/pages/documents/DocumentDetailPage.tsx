import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  compareDocumentParsedCreditReport,
  deleteDocument,
  getAccessToken,
  getDocument,
  getDocumentDuplicateGroup,
  getDocumentDownloadUrl,
  getDocumentOcr,
  getDocumentParsedCreditReport,
  retryDocumentOcr,
  type Document,
  type DocumentDuplicateGroup,
  type DocumentParsedCreditReportComparison,
  type ParsedReportAccountChange,
} from '@verdin/api-client';
import { Badge, Button, Card } from '@verdin/ui';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { DocumentDeleteDialog } from '../../components/documents/DocumentDeleteDialog';
import { DocumentEntityResolutionPanel } from '../../components/documents/DocumentEntityResolutionPanel';
import { DocumentMetadataPanel } from '../../components/documents/DocumentMetadataPanel';
import { DocumentMetadataStatusBadge } from '../../components/documents/DocumentMetadataStatusBadge';
import { DocumentProcessingBadge } from '../../components/documents/DocumentProcessingBadge';
import { ParsedReportTradelines } from '../../components/imports/ParsedReportTradelines';

function formatFileSize(bytes: number | null) {
  if (!bytes) return '—';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value * 100)}%`;
}

function formatCurrency(value: number | null): string {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function changeVariant(
  changeType: ParsedReportAccountChange['change_type'],
): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (changeType === 'added') return 'success';
  if (changeType === 'removed') return 'danger';
  if (changeType === 'changed') return 'warning';
  return 'default';
}

function ParsedReportComparisonPanel({
  comparison,
}: {
  comparison?: DocumentParsedCreditReportComparison;
}) {
  if (!comparison) {
    return null;
  }

  const notableChanges = comparison.account_changes.filter(
    (change) => change.change_type !== 'unchanged',
  );

  return (
    <div className="rounded-md border border-gray-200 p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h4 className="text-sm font-medium text-gray-900">Historical comparison</h4>
          <p className="mt-1 text-sm text-gray-500">
            {comparison.previous_document_id
              ? `Compared with the previous ${comparison.bureau} report for this case.`
              : `No previous ${comparison.bureau} report was found for this case.`}
          </p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs">
          <Badge variant="success">{comparison.summary.added} added</Badge>
          <Badge variant="danger">{comparison.summary.removed} removed</Badge>
          <Badge variant="warning">{comparison.summary.changed} changed</Badge>
          <Badge variant="default">{comparison.summary.unchanged} unchanged</Badge>
        </div>
      </div>

      {notableChanges.length > 0 ? (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="px-3 py-2 font-medium">Change</th>
                <th className="px-3 py-2 font-medium">Creditor</th>
                <th className="px-3 py-2 font-medium">Account</th>
                <th className="px-3 py-2 font-medium">Previous</th>
                <th className="px-3 py-2 font-medium">Current</th>
                <th className="px-3 py-2 font-medium">Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {notableChanges.map((change) => (
                <tr key={change.match_key}>
                  <td className="px-3 py-2">
                    <Badge variant={changeVariant(change.change_type)}>{change.change_type}</Badge>
                  </td>
                  <td className="px-3 py-2 font-medium text-gray-900">
                    {change.creditor_name ?? '—'}
                  </td>
                  <td className="px-3 py-2 text-gray-700">{change.account_number_masked ?? '—'}</td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.previous_balance)}
                  </td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.current_balance)}
                  </td>
                  <td className="px-3 py-2 text-gray-700">
                    {formatCurrency(change.balance_delta)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="mt-3 text-sm text-gray-500">
          No balance or payment status changes were detected.
        </p>
      )}
    </div>
  );
}

function DuplicateDocumentRow({
  document,
  label,
}: {
  document: Document;
  label: 'Canonical' | 'Duplicate';
}) {
  return (
    <li className="flex items-center justify-between gap-3 py-3 text-sm">
      <div>
        <div className="flex items-center gap-2">
          <Badge variant={label === 'Canonical' ? 'success' : 'warning'}>{label}</Badge>
          <Link
            to={`/documents/${document.id}`}
            className="font-medium text-brand-600 hover:underline"
          >
            {document.title}
          </Link>
        </div>
        <p className="mt-1 text-gray-500">
          {document.file_name} · {formatFileSize(document.file_size)} ·{' '}
          {formatDateTime(document.created_at)}
        </p>
      </div>
      <Badge variant="info">v{document.version_number}</Badge>
    </li>
  );
}

function DocumentDuplicatePanel({
  currentDocument,
  duplicateGroup,
}: {
  currentDocument: Document;
  duplicateGroup?: DocumentDuplicateGroup;
}) {
  const hasDuplicates = currentDocument.is_duplicate || (duplicateGroup?.duplicate_count ?? 0) > 0;

  if (!hasDuplicates || !duplicateGroup) {
    return null;
  }

  return (
    <Card title="Duplicate review" className="lg:col-span-3">
      <div className="rounded-md border border-yellow-200 bg-yellow-50 p-3 text-sm text-yellow-900">
        {currentDocument.is_duplicate ? (
          <p>
            This document is an exact duplicate of{' '}
            <Link
              to={`/documents/${duplicateGroup.canonical_document.id}`}
              className="font-medium underline"
            >
              {duplicateGroup.canonical_document.title}
            </Link>
            .
          </p>
        ) : (
          <p>
            This document is the canonical copy for {duplicateGroup.duplicate_count} duplicate
            {duplicateGroup.duplicate_count === 1 ? '' : 's'}.
          </p>
        )}
      </div>
      <ul className="mt-3 divide-y divide-gray-100">
        <DuplicateDocumentRow document={duplicateGroup.canonical_document} label="Canonical" />
        {duplicateGroup.duplicate_documents.map((document) => (
          <DuplicateDocumentRow key={document.id} document={document} label="Duplicate" />
        ))}
      </ul>
    </Card>
  );
}

const ACTIVE_OCR_STATUSES = new Set(['pending', 'queued', 'processing']);

export function DocumentDetailPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId!),
    enabled: Boolean(documentId),
  });

  const { data: ocrData } = useQuery({
    queryKey: ['document-ocr', documentId],
    queryFn: () => getDocumentOcr(documentId!),
    enabled: Boolean(documentId) && Boolean(data) && data?.processing_status !== 'skipped',
    refetchInterval: (query) => {
      const status = query.state.data?.processing_status;
      return status && ACTIVE_OCR_STATUSES.has(status) ? 3000 : false;
    },
  });

  const { data: parsedReport } = useQuery({
    queryKey: ['document-parsed-credit-report', documentId],
    queryFn: () => getDocumentParsedCreditReport(documentId!),
    enabled: Boolean(documentId) && data?.document_type === 'credit_report',
    retry: false,
  });

  const { data: parsedReportComparison } = useQuery({
    queryKey: ['document-parsed-credit-report-comparison', documentId],
    queryFn: () => compareDocumentParsedCreditReport(documentId!),
    enabled: Boolean(documentId) && Boolean(parsedReport),
    retry: false,
  });

  const { data: duplicateGroup } = useQuery({
    queryKey: ['document-duplicates', documentId],
    queryFn: () => getDocumentDuplicateGroup(documentId!),
    enabled: Boolean(documentId) && Boolean(data),
  });

  const retryMutation = useMutation({
    mutationFn: () => retryDocumentOcr(documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document-ocr', documentId] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDocument(documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      navigate('/documents');
    },
  });

  if (!documentId) return null;

  if (isLoading) {
    return (
      <div className="p-8">
        <Card>
          <p className="py-12 text-center text-sm text-gray-500">Loading document...</p>
        </Card>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-8 text-center">
            <p className="text-sm text-red-600">
              {error instanceof Error ? error.message : 'Document not found'}
            </p>
            <Link
              to="/documents"
              className="mt-4 inline-block text-sm text-brand-600 hover:underline"
            >
              Back to documents
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  const processingStatus = ocrData?.processing_status ?? data.processing_status;
  const downloadUrl = getDocumentDownloadUrl(documentId);
  const token = getAccessToken();

  const handleDownload = () => {
    if (!token) return;
    fetch(downloadUrl, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement('a');
        anchor.href = url;
        anchor.download = data.file_name;
        anchor.click();
        URL.revokeObjectURL(url);
      });
  };

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/documents" className="text-sm text-brand-600 hover:underline">
            ← Back to documents
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">{data.title}</h1>
          <p className="text-sm text-gray-500">{data.file_name}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {data.is_duplicate ? (
              <Badge variant="warning">Duplicate</Badge>
            ) : (
              <Badge variant="success">Original</Badge>
            )}
            <Badge variant="info">v{data.version_number}</Badge>
            <DocumentProcessingBadge status={processingStatus} />
            <DocumentMetadataStatusBadge status={data.metadata_status} />
          </div>
        </div>
        <div className="flex gap-2">
          {processingStatus === 'failed' ? (
            <Button
              variant="secondary"
              onClick={() => retryMutation.mutate()}
              disabled={retryMutation.isPending}
            >
              Retry OCR
            </Button>
          ) : null}
          <Button variant="secondary" onClick={handleDownload}>
            Download
          </Button>
          <Button variant="danger" onClick={() => setDeleteOpen(true)}>
            Delete
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <DocumentDuplicatePanel currentDocument={data} duplicateGroup={duplicateGroup} />

        <Card title="File details" className="lg:col-span-1">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-gray-500">File size</dt>
              <dd>{formatFileSize(data.file_size)}</dd>
            </div>
            <div>
              <dt className="text-gray-500">MIME type</dt>
              <dd>{data.mime_type ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-gray-500">SHA-256</dt>
              <dd className="break-all font-mono text-xs">{data.file_hash}</dd>
            </div>
            <div>
              <dt className="text-gray-500">Uploaded</dt>
              <dd>{formatDateTime(data.created_at)}</dd>
            </div>
            {ocrData?.ocr_processed_at ? (
              <div>
                <dt className="text-gray-500">OCR processed</dt>
                <dd>{formatDateTime(ocrData.ocr_processed_at)}</dd>
              </div>
            ) : null}
            <div>
              <dt className="text-gray-500">Case</dt>
              <dd>
                <Link to={`/cases/${data.case_id}`} className="text-brand-600 hover:underline">
                  View case
                </Link>
              </dd>
            </div>
          </dl>
          {data.description ? (
            <p className="mt-4 text-sm text-gray-600">{data.description}</p>
          ) : null}
        </Card>

        <DocumentMetadataPanel documentId={documentId} hasOcrText={Boolean(ocrData?.ocr_text)} />

        <DocumentEntityResolutionPanel
          documentId={documentId}
          hasMetadata={data.metadata_status === 'extracted'}
        />

        {data.document_type === 'credit_report' ? (
          <Card title="Parsed credit report" className="lg:col-span-3">
            {parsedReport ? (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2 text-sm">
                  <Badge variant={parsedReport.is_partial ? 'warning' : 'success'}>
                    {parsedReport.is_partial ? 'Partial parse' : 'Complete parse'}
                  </Badge>
                  <span className="text-gray-700">
                    {parsedReport.parser_name} ({parsedReport.bureau})
                  </span>
                  <span className="text-gray-500">
                    {formatPercent(parsedReport.parser_confidence)} confidence
                  </span>
                  <span className="text-gray-500">
                    Parsed {formatDateTime(parsedReport.parsed_at)}
                  </span>
                </div>
                {parsedReport.warnings.length > 0 ? (
                  <p className="rounded-md bg-yellow-50 p-3 text-sm text-yellow-800">
                    Parser warnings: {parsedReport.warnings.join(', ')}
                  </p>
                ) : null}
                <ParsedReportComparisonPanel comparison={parsedReportComparison} />
                <ParsedReportTradelines parsedReport={parsedReport} />
              </div>
            ) : (
              <p className="text-sm text-gray-500">
                Structured parser output is not available for this credit report yet.
              </p>
            )}
          </Card>
        ) : null}

        <Card title="Extracted text" className="lg:col-span-2 lg:row-start-1 lg:col-start-2">
          {processingStatus === 'skipped' ? (
            <p className="text-sm text-gray-500">This file format is not processed by OCR.</p>
          ) : null}
          {ACTIVE_OCR_STATUSES.has(processingStatus) ? (
            <p className="text-sm text-gray-500">
              OCR is running in the background. This page refreshes automatically.
            </p>
          ) : null}
          {processingStatus === 'failed' && ocrData?.ocr_error ? (
            <p className="mb-4 text-sm text-red-600">{ocrData.ocr_error}</p>
          ) : null}
          {ocrData?.ocr_text ? (
            <pre className="max-h-[480px] overflow-auto whitespace-pre-wrap rounded-md bg-gray-50 p-4 text-sm text-gray-800">
              {ocrData.ocr_text}
            </pre>
          ) : null}
          {!ocrData?.ocr_text &&
          processingStatus !== 'skipped' &&
          !ACTIVE_OCR_STATUSES.has(processingStatus) ? (
            <p className="text-sm text-gray-500">No text was extracted from this document.</p>
          ) : null}
        </Card>

        {data.versions && data.versions.length > 0 ? (
          <Card title="Version history" className="lg:col-span-3">
            <ul className="divide-y divide-gray-100">
              {data.versions.map((version) => (
                <li key={version.id} className="flex items-center justify-between py-3 text-sm">
                  <div>
                    <p className="font-medium text-gray-900">
                      v{version.version_number} — {version.file_name}
                    </p>
                    <p className="text-gray-500">{formatDateTime(version.created_at)}</p>
                  </div>
                  <p className="text-gray-600">{formatFileSize(version.file_size)}</p>
                </li>
              ))}
            </ul>
          </Card>
        ) : null}
      </div>

      <DocumentDeleteDialog
        title={data.title}
        open={deleteOpen}
        loading={deleteMutation.isPending}
        onConfirm={() => deleteMutation.mutate()}
        onCancel={() => setDeleteOpen(false)}
      />
    </div>
  );
}
