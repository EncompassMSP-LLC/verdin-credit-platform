import type { CasePriority, CaseStatus } from '@verdin/shared';
import { CASE_PRIORITY_LABELS, CASE_STATUS_LABELS } from '@verdin/shared';
import { Badge } from '@verdin/ui';

const statusVariants: Record<CaseStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
  open: 'info',
  active: 'info',
  on_hold: 'warning',
  resolved: 'success',
  closed: 'default',
};

const priorityVariants: Record<
  CasePriority,
  'default' | 'success' | 'warning' | 'danger' | 'info'
> = {
  low: 'default',
  medium: 'info',
  high: 'warning',
  critical: 'danger',
};

export function CaseStatusChip({ status }: { status: CaseStatus }) {
  return <Badge variant={statusVariants[status]}>{CASE_STATUS_LABELS[status]}</Badge>;
}

export function CasePriorityBadge({ priority }: { priority: CasePriority }) {
  return <Badge variant={priorityVariants[priority]}>{CASE_PRIORITY_LABELS[priority]}</Badge>;
}
