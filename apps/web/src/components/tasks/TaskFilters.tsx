import {
  TASK_PRIORITIES,
  TASK_PRIORITY_LABELS,
  TASK_STATUSES,
  TASK_STATUS_LABELS,
  type TaskPriority,
  type TaskStatus,
} from '@verdin/shared';

export interface TaskFiltersValue {
  search: string;
  status: TaskStatus | '';
  priority: TaskPriority | '';
  overdue: boolean;
  sort_by: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order: 'asc' | 'desc';
}

interface TaskFiltersProps {
  value: TaskFiltersValue;
  onChange: (value: TaskFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function TaskFilters({ value, onChange }: TaskFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      <div className="lg:col-span-2">
        <label className="block text-sm font-medium text-gray-700" htmlFor="task-search">
          Search
        </label>
        <input
          id="task-search"
          className={inputClass}
          placeholder="Search title or description"
          value={value.search}
          onChange={(e) => onChange({ ...value, search: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700" htmlFor="task-status">
          Status
        </label>
        <select
          id="task-status"
          className={inputClass}
          value={value.status}
          onChange={(e) =>
            onChange({ ...value, status: e.target.value as TaskFiltersValue['status'] })
          }
        >
          <option value="">All statuses</option>
          {TASK_STATUSES.map((status) => (
            <option key={status} value={status}>
              {TASK_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700" htmlFor="task-priority">
          Priority
        </label>
        <select
          id="task-priority"
          className={inputClass}
          value={value.priority}
          onChange={(e) =>
            onChange({ ...value, priority: e.target.value as TaskFiltersValue['priority'] })
          }
        >
          <option value="">All priorities</option>
          {TASK_PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {TASK_PRIORITY_LABELS[priority]}
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-end">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input
            type="checkbox"
            checked={value.overdue}
            onChange={(e) => onChange({ ...value, overdue: e.target.checked })}
          />
          Overdue only
        </label>
      </div>
    </div>
  );
}
