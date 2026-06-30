import type { MetadataStatus } from '@verdin/shared';
import { METADATA_STATUS_LABELS } from '@verdin/shared';
import { Badge } from '@verdin/ui';

const VARIANT: Record<MetadataStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
  pending: 'warning',
  extracted: 'success',
  failed: 'danger',
};

interface DocumentMetadataStatusBadgeProps {
  status: MetadataStatus | null | undefined;
}

export function DocumentMetadataStatusBadge({ status }: DocumentMetadataStatusBadgeProps) {
  if (!status) {
    return <Badge variant="default">No metadata</Badge>;
  }
  return <Badge variant={VARIANT[status]}>{METADATA_STATUS_LABELS[status]}</Badge>;
}
