import type { ClassificationMethod, DocumentType } from '@verdin/shared';
import {
  CLASSIFICATION_METHOD_LABELS,
  DOCUMENT_TYPE_LABELS,
  formatConfidenceScore,
} from '@verdin/shared';
import { Badge } from '@verdin/ui';

const TYPE_VARIANT: Record<DocumentType, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
  credit_report: 'info',
  collection_letter: 'warning',
  bureau_response: 'info',
  identity_document: 'success',
  proof_of_address: 'success',
  bankruptcy: 'danger',
  court_record: 'warning',
  medical_collection: 'warning',
  utility_bill: 'default',
  unknown: 'default',
};

interface DocumentClassificationBadgeProps {
  documentType: DocumentType | null | undefined;
  confidenceScore?: number | null;
  classificationMethod?: ClassificationMethod | null;
}

export function DocumentClassificationBadge({
  documentType,
  confidenceScore,
  classificationMethod,
}: DocumentClassificationBadgeProps) {
  if (!documentType) {
    return <Badge variant="default">Unclassified</Badge>;
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Badge variant={TYPE_VARIANT[documentType]}>{DOCUMENT_TYPE_LABELS[documentType]}</Badge>
      {confidenceScore !== null && confidenceScore !== undefined ? (
        <span className="text-xs text-gray-500">{formatConfidenceScore(confidenceScore)}</span>
      ) : null}
      {classificationMethod ? (
        <span className="text-xs text-gray-400">
          {CLASSIFICATION_METHOD_LABELS[classificationMethod]}
        </span>
      ) : null}
    </div>
  );
}
