import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  deleteDocument,
  getAccessToken,
  getDocument,
  getDocumentDownloadUrl,
  getDocumentOcr,
  getDocumentParsedCreditReport,
  retryDocumentOcr,
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
