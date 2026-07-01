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
  source_module: string;
  overdue: boolean;
  sort_by: 'created_at' | 'due_date' | 'priority' | 'title';
  sort_order: 'asc' | 'desc';
}

const TASK_SOURCE_MODULE_OPTIONS = [
  { value: 'accounts.dispute_draft', label: 'Dispute draft review' },
  { value: 'accounts.dispute_letter', label: 'Dispute letter review' },
  { value: 'accounts.dispute_letter_followup', label: 'CRA response follow-up' },
  { value: 'documents.parsed_credit_report', label: 'Parsed report review' },
] as const;

interface TaskFiltersProps {
  value: TaskFiltersValue;
  onChange: (value: TaskFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function TaskFilters({ value, onChange }: TaskFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
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
      <div>
        <label className="block text-sm font-medium text-gray-700" htmlFor="task-source-module">
          Source
        </label>
        <select
          id="task-source-module"
          className={inputClass}
          value={value.source_module}
          onChange={(e) => onChange({ ...value, source_module: e.target.value })}
        >
          <option value="">All sources</option>
          {TASK_SOURCE_MODULE_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
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
