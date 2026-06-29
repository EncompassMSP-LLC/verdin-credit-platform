import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { classifyDocument, getClassification, reclassifyDocument } from '@verdin/api-client';
import {
  CLASSIFICATION_METHOD_LABELS,
  DOCUMENT_TYPE_LABELS,
  formatConfidenceScore,
} from '@verdin/shared';
import { Badge, Button, Card } from '@verdin/ui';
import { DocumentClassificationBadge } from './DocumentClassificationBadge';

function formatDateTime(value: string) {
  return new Date(value).toLocaleString();
}

interface DocumentClassificationPanelProps {
  documentId: string;
  documentType?: string | null;
  confidenceScore?: number | null;
  classificationMethod?: string | null;
  classifiedAt?: string | null;
}

export function DocumentClassificationPanel({
  documentId,
  documentType,
  confidenceScore,
  classificationMethod,
  classifiedAt,
}: DocumentClassificationPanelProps) {
  const queryClient = useQueryClient();

  const { data: classification } = useQuery({
    queryKey: ['document-classification', documentId],
    queryFn: () => getClassification(documentId),
    initialData:
      documentType || confidenceScore || classificationMethod || classifiedAt
        ? {
            document_id: documentId,
            document_type: (documentType as never) ?? null,
            confidence_score: confidenceScore ?? null,
            classification_method: (classificationMethod as never) ?? null,
            classified_at: classifiedAt ?? null,
            classified_by_id: null,
          }
        : undefined,
  });

  const classifyMutation = useMutation({
    mutationFn: () => classifyDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document-classification', documentId] });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const reclassifyMutation = useMutation({
    mutationFn: () => reclassifyDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['document', documentId] });
      queryClient.invalidateQueries({ queryKey: ['document-classification', documentId] });
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
  });

  const result = classification;
  const isClassified = Boolean(result?.document_type);
  const isPending = classifyMutation.isPending || reclassifyMutation.isPending;

  return (
    <Card title="Classification">
      <div className="space-y-4">
        <DocumentClassificationBadge
          documentType={result?.document_type}
          confidenceScore={result?.confidence_score}
          classificationMethod={result?.classification_method}
        />

        <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-gray-500">Confidence</dt>
            <dd className="font-medium">{formatConfidenceScore(result?.confidence_score)}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Method</dt>
            <dd>
              {result?.classification_method ? (
                <Badge variant="info">
                  {CLASSIFICATION_METHOD_LABELS[result.classification_method]}
                </Badge>
              ) : (
                '—'
              )}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Document type</dt>
            <dd>
              {result?.document_type
                ? DOCUMENT_TYPE_LABELS[result.document_type]
                : 'Not classified'}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Classified at</dt>
            <dd>{result?.classified_at ? formatDateTime(result.classified_at) : '—'}</dd>
          </div>
        </dl>

        <div className="flex flex-wrap gap-2">
          {!isClassified ? (
            <Button onClick={() => classifyMutation.mutate()} disabled={isPending}>
              Classify Now
            </Button>
          ) : (
            <Button
              variant="secondary"
              onClick={() => reclassifyMutation.mutate()}
              disabled={isPending}
            >
              Reclassify
            </Button>
          )}
        </div>

        {classifyMutation.isError || reclassifyMutation.isError ? (
          <p className="text-sm text-red-600">
            {classifyMutation.error instanceof Error
              ? classifyMutation.error.message
              : reclassifyMutation.error instanceof Error
                ? reclassifyMutation.error.message
                : 'Classification failed'}
          </p>
        ) : null}
      </div>
    </Card>
  );
}
