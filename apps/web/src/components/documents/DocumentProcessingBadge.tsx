import type { DocumentProcessingStatus } from '@verdin/shared';
import { DOCUMENT_PROCESSING_STATUS_LABELS } from '@verdin/shared';
import { Badge } from '@verdin/ui';

const STATUS_VARIANT: Record<
  DocumentProcessingStatus,
  'default' | 'success' | 'warning' | 'danger' | 'info'
> = {
  pending: 'default',
  queued: 'info',
  processing: 'info',
  completed: 'success',
  failed: 'danger',
  skipped: 'default',
};

interface DocumentProcessingBadgeProps {
  status: DocumentProcessingStatus;
}

export function DocumentProcessingBadge({ status }: DocumentProcessingBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANT[status]}>{DOCUMENT_PROCESSING_STATUS_LABELS[status]}</Badge>
  );
}
