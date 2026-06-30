import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  extractDocumentMetadata,
  getDocumentMetadata,
  type DocumentMetadata,
} from '@verdin/api-client';
import { METADATA_STATUS_LABELS } from '@verdin/shared';
import { Badge, Button, Card } from '@verdin/ui';
import { DocumentMetadataStatusBadge } from './DocumentMetadataStatusBadge';

interface DocumentMetadataPanelProps {
  documentId: string;
  hasOcrText: boolean;
}

function formatCurrency(value: number | null) {
  if (value === null) return '—';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
}

function MetadataFields({ metadata }: { metadata: DocumentMetadata }) {
  const fields: Array<{ label: string; value: string | null | undefined }> = [
    { label: 'Consumer name', value: metadata.consumer_name },
    { label: 'Bureau', value: metadata.bureau },
    { label: 'Creditor', value: metadata.creditor },
    { label: 'Collection agency', value: metadata.collection_agency },
    { label: 'Account number', value: metadata.account_number_masked },
    { label: 'Report date', value: metadata.report_date },
    { label: 'Balance', value: formatCurrency(metadata.balance) },
    { label: 'Payment status', value: metadata.payment_status },
    { label: 'SSN (masked)', value: metadata.ssn_masked },
  ];

  return (
    <dl className="space-y-3 text-sm">
      {fields.map((field) => (
        <div key={field.label}>
          <dt className="text-gray-500">{field.label}</dt>
          <dd>{field.value ?? '—'}</dd>
        </div>
      ))}
      {metadata.addresses.length > 0 ? (
        <div>
          <dt className="text-gray-500">Addresses</dt>
          <dd className="space-y-1">
            {metadata.addresses.map((address) => (
              <p key={address}>{address}</p>
            ))}
          </dd>
        </div>
      ) : null}
      {metadata.phone_numbers.length > 0 ? (
        <div>
          <dt className="text-gray-500">Phone numbers</dt>
          <dd>{metadata.phone_numbers.join(', ')}</dd>
        </div>
      ) : null}
      <div>
        <dt className="text-gray-500">Confidence</dt>
        <dd>
          {metadata.confidence_score !== null
            ? `${Math.round(metadata.confidence_score * 100)}%`
            : '—'}
        </dd>
      </div>
      <div>
        <dt className="text-gray-500">Status</dt>
        <dd>
          <DocumentMetadataStatusBadge status={metadata.metadata_status} />
        </dd>
      </div>
      {metadata.extracted_at ? (
        <div>
          <dt className="text-gray-500">Extracted</dt>
          <dd>{new Date(metadata.extracted_at).toLocaleString()}</dd>
        </div>
      ) : null}
      {metadata.extraction_error ? (
        <p className="text-sm text-red-600">{metadata.extraction_error}</p>
      ) : null}
    </dl>
  );
}

export function DocumentMetadataPanel({ documentId, hasOcrText }: DocumentMetadataPanelProps) {
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['document-metadata', documentId],
    queryFn: () => getDocumentMetadata(documentId),
    enabled: hasOcrText,
    retry: false,
  });

  const extractMutation = useMutation({
    mutationFn: () => extractDocumentMetadata(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document-metadata', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document-resolutions', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
    },
  });

  if (!hasOcrText) {
    return (
      <Card title="Extracted metadata">
        <p className="text-sm text-gray-500">OCR text is required before metadata extraction.</p>
      </Card>
    );
  }

  return (
    <Card title="Extracted metadata">
      <div className="mb-4 flex justify-end">
        <Button
          variant="secondary"
          size="sm"
          onClick={() => extractMutation.mutate()}
          disabled={extractMutation.isPending}
        >
          {data ? 'Re-extract' : 'Extract'}
        </Button>
      </div>
      {isLoading ? <p className="text-sm text-gray-500">Loading metadata...</p> : null}
      {isError ? (
        <div className="space-y-3">
          <p className="text-sm text-gray-500">
            {error instanceof Error && error.message.includes('404')
              ? 'Metadata has not been extracted yet.'
              : error instanceof Error
                ? error.message
                : 'Failed to load metadata'}
          </p>
          <Button variant="secondary" size="sm" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      ) : null}
      {data ? <MetadataFields metadata={data} /> : null}
      {extractMutation.isError ? (
        <p className="mt-3 text-sm text-red-600">
          {extractMutation.error instanceof Error
            ? extractMutation.error.message
            : 'Extraction failed'}
        </p>
      ) : null}
      {data?.metadata_status ? (
        <div className="mt-4 flex items-center gap-2 text-xs text-gray-500">
          <Badge variant="info">{METADATA_STATUS_LABELS[data.metadata_status]}</Badge>
          <span>via {data.extraction_method}</span>
        </div>
      ) : null}
    </Card>
  );
}
