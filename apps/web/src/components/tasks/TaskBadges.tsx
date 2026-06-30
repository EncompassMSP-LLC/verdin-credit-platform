import type { TaskPriority, TaskStatus } from '@verdin/shared';
import { TASK_PRIORITY_LABELS, TASK_STATUS_LABELS } from '@verdin/shared';
import { Badge } from '@verdin/ui';

const statusVariants: Record<TaskStatus, 'default' | 'success' | 'warning' | 'danger' | 'info'> = {
  open: 'info',
  in_progress: 'warning',
  blocked: 'danger',
  completed: 'success',
  canceled: 'default',
};

const priorityVariants: Record<
  TaskPriority,
  'default' | 'success' | 'warning' | 'danger' | 'info'
> = {
  low: 'default',
  medium: 'info',
  high: 'warning',
  critical: 'danger',
};

export function TaskStatusChip({ status }: { status: TaskStatus }) {
  return <Badge variant={statusVariants[status]}>{TASK_STATUS_LABELS[status]}</Badge>;
}

export function TaskPriorityBadge({ priority }: { priority: TaskPriority }) {
  return <Badge variant={priorityVariants[priority]}>{TASK_PRIORITY_LABELS[priority]}</Badge>;
}

export function TaskOverdueBadge() {
  return <Badge variant="danger">Overdue</Badge>;
}
