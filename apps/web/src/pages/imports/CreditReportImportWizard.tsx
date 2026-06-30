import { useMemo, useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  ApiClientError,
  getDocument,
  getDocumentMetadata,
  getDocumentOcr,
  getDocumentParsedCreditReport,
  getDocumentResolutions,
  listCases,
  resolveDocumentEntities,
  type Document,
  type DocumentEntityResolution,
  type DocumentMetadata,
  type DocumentOcrResult,
  type DocumentParsedCreditReport,
  uploadDocument,
} from '@verdin/api-client';
import { Button, Card, Badge } from '@verdin/ui';
import { Link } from 'react-router-dom';
import { DocumentMetadataStatusBadge } from '../../components/documents/DocumentMetadataStatusBadge';
import { DocumentProcessingBadge } from '../../components/documents/DocumentProcessingBadge';
import { featureFlags } from '../../lib/feature-flags';

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

const ACTIVE_OCR_STATUSES = new Set(['pending', 'queued', 'processing']);

type StepStatus = 'pending' | 'active' | 'complete' | 'failed';

function isNotFound(error: unknown): boolean {
  return error instanceof ApiClientError && error.status === 404;
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—';
  return `${Math.round(value * 100)}%`;
}

function statusVariant(status: StepStatus): 'default' | 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'complete') return 'success';
  if (status === 'active') return 'info';
  if (status === 'failed') return 'danger';
  return 'default';
}

function StepCard({
  title,
  status,
  children,
}: {
  title: string;
  status: StepStatus;
  children: React.ReactNode;
}) {
  const label =
    status === 'complete'
      ? 'Complete'
      : status === 'active'
        ? 'Running'
        : status === 'failed'
          ? 'Needs attention'
          : 'Waiting';

  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <div className="mt-3">{children}</div>
        </div>
        <Badge variant={statusVariant(status)}>{label}</Badge>
      </div>
    </Card>
  );
}

function MetadataSummary({ metadata }: { metadata: DocumentMetadata }) {
  return (
    <dl className="grid gap-3 text-sm sm:grid-cols-2">
      <div>
        <dt className="text-gray-500">Consumer</dt>
        <dd>{metadata.consumer_name ?? '—'}</dd>
      </div>
      <div>
        <dt className="text-gray-500">Bureau</dt>
        <dd>{metadata.bureau ?? '—'}</dd>
      </div>
      <div>
        <dt className="text-gray-500">Creditor</dt>
        <dd>{metadata.creditor ?? '—'}</dd>
      </div>
      <div>
        <dt className="text-gray-500">Account</dt>
        <dd>{metadata.account_number_masked ?? '—'}</dd>
      </div>
      <div>
        <dt className="text-gray-500">Report date</dt>
        <dd>{metadata.report_date ?? '—'}</dd>
      </div>
      <div>
        <dt className="text-gray-500">Confidence</dt>
        <dd>{formatPercent(metadata.confidence_score)}</dd>
      </div>
    </dl>
  );
}

function ParserSummary({ parsedReport }: { parsedReport: DocumentParsedCreditReport }) {
  return (
    <div className="rounded-md border border-blue-100 bg-blue-50 p-3 text-sm text-blue-900">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-medium">
          Parsed by {parsedReport.parser_name} ({parsedReport.bureau})
        </span>
        <Badge variant={parsedReport.is_partial ? 'warning' : 'success'}>
          {parsedReport.is_partial ? 'Partial' : 'Complete'}
        </Badge>
        <span>{formatPercent(parsedReport.parser_confidence)} confidence</span>
      </div>
      {parsedReport.warnings.length > 0 ? (
        <p className="mt-2 text-blue-800">Warnings: {parsedReport.warnings.join(', ')}</p>
      ) : null}
    </div>
  );
}

function ResolutionLinks({ resolutions }: { resolutions: DocumentEntityResolution[] }) {
  const linked = resolutions.filter((resolution) => resolution.matched_entity_id);

  if (linked.length === 0) {
    return <p className="text-sm text-gray-500">No matched case or account yet.</p>;
  }

  return (
    <ul className="space-y-2 text-sm">
      {linked.map((resolution) => {
        const href =
          resolution.entity_type === 'case'
            ? `/cases/${resolution.matched_entity_id}`
            : resolution.entity_type === 'account'
              ? `/accounts/${resolution.matched_entity_id}`
              : null;

        return (
          <li key={resolution.id} className="flex items-center justify-between gap-3">
            <span className="capitalize text-gray-700">
              {resolution.entity_type} match ({formatPercent(resolution.confidence_score)})
            </span>
            {href ? (
              <Link to={href} className="text-brand-600 hover:underline">
                View match
              </Link>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}

export function CreditReportImportWizard() {
  const queryClient = useQueryClient();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [caseId, setCaseId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [documentId, setDocumentId] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const casesQuery = useQuery({
    queryKey: ['cases-for-credit-report-import'],
    queryFn: () => listCases({ page_size: 100 }),
  });

  const documentQuery = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId!),
    enabled: Boolean(documentId),
    refetchInterval: (query) => {
      const document = query.state.data as Document | undefined;
      return document?.metadata_status !== 'extracted' ? 3000 : false;
    },
  });

  const ocrQuery = useQuery({
    queryKey: ['document-ocr', documentId],
    queryFn: () => getDocumentOcr(documentId!),
    enabled: Boolean(documentId),
    refetchInterval: (query) => {
      const ocr = query.state.data as DocumentOcrResult | undefined;
      return ocr?.processing_status && ACTIVE_OCR_STATUSES.has(ocr.processing_status)
        ? 3000
        : false;
    },
  });

  const metadataQuery = useQuery({
    queryKey: ['document-metadata', documentId],
    queryFn: () => getDocumentMetadata(documentId!),
    enabled: Boolean(documentId) && Boolean(ocrQuery.data?.ocr_text),
    retry: false,
    refetchInterval: (query) => {
      const metadata = query.state.data as DocumentMetadata | undefined;
      return metadata?.metadata_status === 'extracted' ? false : 3000;
    },
  });

  const parsedReportQuery = useQuery({
    queryKey: ['document-parsed-credit-report', documentId],
    queryFn: () => getDocumentParsedCreditReport(documentId!),
    enabled: Boolean(documentId) && Boolean(ocrQuery.data?.ocr_text),
    retry: false,
    refetchInterval: (query) => (query.state.data ? false : 3000),
  });

  const resolutionsQuery = useQuery({
    queryKey: ['document-resolutions', documentId],
    queryFn: () => getDocumentResolutions(documentId!),
    enabled: Boolean(documentId) && metadataQuery.data?.metadata_status === 'extracted',
    retry: false,
    refetchInterval: (query) => {
      const resolutions = query.state.data?.resolutions ?? [];
      return resolutions.length > 0 ? false : 3000;
    },
  });

  const uploadMutation = useMutation({
    mutationFn: () => {
      if (!file || !caseId || !title.trim()) {
        throw new Error('Title, case, and PDF file are required');
      }
      if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
        throw new Error('Credit report imports currently accept PDF files only');
      }
      return uploadDocument({
        file,
        title: title.trim(),
        case_id: caseId,
        description: description.trim() || 'Imported via Credit Report Import Wizard',
      });
    },
    onSuccess: (document) => {
      setDocumentId(document.id);
      setFormError(null);
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error: Error) => setFormError(error.message),
  });

  const resolveMutation = useMutation({
    mutationFn: () => resolveDocumentEntities(documentId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-resolutions', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
    },
  });

  const selectedCase = useMemo(
    () => casesQuery.data?.items.find((caseItem) => caseItem.id === caseId),
    [caseId, casesQuery.data?.items],
  );

  const processingStatus =
    ocrQuery.data?.processing_status ?? documentQuery.data?.processing_status ?? 'pending';
  const uploadStatus: StepStatus = documentId
    ? 'complete'
    : uploadMutation.isPending
      ? 'active'
      : 'pending';
  const ocrStatus: StepStatus =
    processingStatus === 'failed'
      ? 'failed'
      : ocrQuery.data?.ocr_text
        ? 'complete'
        : documentId
          ? 'active'
          : 'pending';
  const metadataStatus: StepStatus =
    metadataQuery.data?.metadata_status === 'extracted'
      ? 'complete'
      : metadataQuery.error && !isNotFound(metadataQuery.error)
        ? 'failed'
        : ocrQuery.data?.ocr_text
          ? 'active'
          : 'pending';
  const resolutionStatus: StepStatus =
    (resolutionsQuery.data?.resolutions.length ?? 0) > 0
      ? 'complete'
      : resolutionsQuery.error && !isNotFound(resolutionsQuery.error)
        ? 'failed'
        : metadataQuery.data?.metadata_status === 'extracted'
          ? 'active'
          : 'pending';

  if (!featureFlags.enableImports) {
    return (
      <div className="p-8">
        <Card>
          <div className="py-12 text-center">
            <h1 className="text-xl font-semibold text-gray-900">Imports are not enabled</h1>
            <p className="mt-2 text-sm text-gray-500">
              Enable VITE_ENABLE_IMPORTS to use the Credit Report Import Wizard.
            </p>
            <Link to="/documents" className="mt-4 inline-block">
              <Button variant="secondary">Back to documents</Button>
            </Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link to="/documents" className="text-sm text-brand-600 hover:underline">
            ← Back to documents
          </Link>
          <h1 className="mt-2 text-2xl font-bold text-gray-900">Credit Report Import Wizard</h1>
          <p className="mt-1 text-gray-500">
            Upload a bureau PDF and track OCR, structured parsing, metadata extraction, and entity
            matching.
          </p>
        </div>
        {documentId ? (
          <Link to={`/documents/${documentId}`}>
            <Button variant="secondary">View document</Button>
          </Link>
        ) : null}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card title="Import details" className="lg:col-span-1">
          <form
            className="space-y-4"
            onSubmit={(event) => {
              event.preventDefault();
              setFormError(null);
              uploadMutation.mutate();
            }}
          >
            <div>
              <label htmlFor="import-title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                id="import-title"
                className={inputClass}
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Equifax credit report"
                disabled={Boolean(documentId)}
                required
              />
            </div>

            <div>
              <label htmlFor="import-case" className="block text-sm font-medium text-gray-700">
                Case
              </label>
              <select
                id="import-case"
                className={inputClass}
                value={caseId}
                onChange={(event) => setCaseId(event.target.value)}
                disabled={Boolean(documentId)}
                required
              >
                <option value="">Select a case</option>
                {casesQuery.data?.items.map((caseItem) => (
                  <option key={caseItem.id} value={caseItem.id}>
                    {caseItem.title} ({caseItem.client_name})
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="import-description"
                className="block text-sm font-medium text-gray-700"
              >
                Notes
              </label>
              <textarea
                id="import-description"
                rows={3}
                className={inputClass}
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                disabled={Boolean(documentId)}
              />
            </div>

            <div>
              <label htmlFor="import-file" className="block text-sm font-medium text-gray-700">
                Credit report PDF
              </label>
              <input
                id="import-file"
                type="file"
                className={inputClass}
                accept=".pdf,application/pdf"
                onChange={(event) => {
                  const nextFile = event.target.files?.[0] ?? null;
                  setFile(nextFile);
                  if (nextFile && !title.trim()) {
                    setTitle(nextFile.name.replace(/\.[^.]+$/, ''));
                  }
                }}
                disabled={Boolean(documentId)}
                required
              />
              <p className="mt-1 text-xs text-gray-500">
                Experian and Equifax PDFs are parsed into the canonical credit report model.
              </p>
            </div>

            {selectedCase ? (
              <p className="rounded-md bg-blue-50 p-3 text-sm text-blue-700">
                Importing into {selectedCase.title} for {selectedCase.client_name}.
              </p>
            ) : null}

            {formError ? (
              <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{formError}</div>
            ) : null}

            <Button type="submit" loading={uploadMutation.isPending} disabled={Boolean(documentId)}>
              Start import
            </Button>
          </form>
        </Card>

        <div className="space-y-4 lg:col-span-2">
          <StepCard title="1. Upload document" status={uploadStatus}>
            {documentQuery.data ? (
              <div className="space-y-2 text-sm">
                <p>
                  Uploaded <span className="font-medium">{documentQuery.data.file_name}</span>.
                </p>
                <div className="flex flex-wrap gap-2">
                  <DocumentProcessingBadge status={processingStatus} />
                  {documentQuery.data.metadata_status ? (
                    <DocumentMetadataStatusBadge status={documentQuery.data.metadata_status} />
                  ) : null}
                </div>
              </div>
            ) : (
              <p className="text-sm text-gray-500">Choose a case and PDF to begin.</p>
            )}
          </StepCard>

          <StepCard title="2. OCR and classification" status={ocrStatus}>
            {ocrQuery.data?.ocr_text ? (
              <p className="text-sm text-gray-600">
                OCR completed with {ocrQuery.data.ocr_text.length.toLocaleString()} characters of
                extracted text.
              </p>
            ) : ocrStatus === 'active' ? (
              <p className="text-sm text-gray-500">OCR and classification are running.</p>
            ) : ocrStatus === 'failed' ? (
              <p className="text-sm text-red-600">
                {ocrQuery.data?.ocr_error ?? 'OCR failed. Open the document to retry.'}
              </p>
            ) : (
              <p className="text-sm text-gray-500">Waiting for upload.</p>
            )}
          </StepCard>

          <StepCard title="3. Parse and extract metadata" status={metadataStatus}>
            {metadataQuery.data ? (
              <div className="space-y-4">
                {parsedReportQuery.data ? (
                  <ParserSummary parsedReport={parsedReportQuery.data} />
                ) : null}
                <MetadataSummary metadata={metadataQuery.data} />
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <DocumentMetadataStatusBadge status={metadataQuery.data.metadata_status} />
                  <span>via {metadataQuery.data.extraction_method}</span>
                </div>
              </div>
            ) : metadataStatus === 'active' ? (
              <p className="text-sm text-gray-500">
                The worker is parsing the report and bridging structured fields into metadata.
              </p>
            ) : metadataStatus === 'failed' ? (
              <p className="text-sm text-red-600">
                {metadataQuery.error instanceof Error
                  ? metadataQuery.error.message
                  : 'Metadata extraction failed'}
              </p>
            ) : (
              <p className="text-sm text-gray-500">Waiting for OCR text.</p>
            )}
          </StepCard>

          <StepCard title="4. Match case and account" status={resolutionStatus}>
            {resolutionsQuery.data ? (
              <div className="space-y-4">
                <ResolutionLinks resolutions={resolutionsQuery.data.resolutions} />
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => resolveMutation.mutate()}
                  loading={resolveMutation.isPending}
                >
                  Re-run matching
                </Button>
              </div>
            ) : resolutionStatus === 'active' ? (
              <div className="space-y-3">
                <p className="text-sm text-gray-500">
                  Entity resolution is queued after metadata extraction.
                </p>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => resolveMutation.mutate()}
                  loading={resolveMutation.isPending}
                >
                  Run matching now
                </Button>
              </div>
            ) : resolutionStatus === 'failed' ? (
              <p className="text-sm text-red-600">
                {resolutionsQuery.error instanceof Error
                  ? resolutionsQuery.error.message
                  : 'Entity resolution failed'}
              </p>
            ) : (
              <p className="text-sm text-gray-500">Waiting for metadata.</p>
            )}
          </StepCard>
        </div>
      </div>
    </div>
  );
}
