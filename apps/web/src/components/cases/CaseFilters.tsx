import type { CasePriority, CaseStage, CaseStatus } from '@verdin/shared';
import {
  CASE_PRIORITIES,
  CASE_PRIORITY_LABELS,
  CASE_STAGES,
  CASE_STAGE_LABELS,
  CASE_STATUSES,
  CASE_STATUS_LABELS,
} from '@verdin/shared';

export interface CaseFiltersValue {
  search: string;
  status: CaseStatus | '';
  stage: CaseStage | '';
  priority: CasePriority | '';
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

interface CaseFiltersProps {
  value: CaseFiltersValue;
  onChange: (value: CaseFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function CaseFilters({ value, onChange }: CaseFiltersProps) {
  const update = (patch: Partial<CaseFiltersValue>) => onChange({ ...value, ...patch });

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-6">
      <div className="lg:col-span-2">
        <label htmlFor="case-search" className="mb-1 block text-sm font-medium text-gray-700">
          Search
        </label>
        <input
          id="case-search"
          type="search"
          placeholder="Title, client, case number..."
          className={inputClass}
          value={value.search}
          onChange={(e) => update({ search: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="case-status" className="mb-1 block text-sm font-medium text-gray-700">
          Status
        </label>
        <select
          id="case-status"
          className={inputClass}
          value={value.status}
          onChange={(e) => update({ status: e.target.value as CaseStatus | '' })}
        >
          <option value="">All statuses</option>
          {CASE_STATUSES.map((status) => (
            <option key={status} value={status}>
              {CASE_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="case-stage" className="mb-1 block text-sm font-medium text-gray-700">
          Stage
        </label>
        <select
          id="case-stage"
          className={inputClass}
          value={value.stage}
          onChange={(e) => update({ stage: e.target.value as CaseStage | '' })}
        >
          <option value="">All stages</option>
          {CASE_STAGES.map((stage) => (
            <option key={stage} value={stage}>
              {CASE_STAGE_LABELS[stage]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="case-priority" className="mb-1 block text-sm font-medium text-gray-700">
          Priority
        </label>
        <select
          id="case-priority"
          className={inputClass}
          value={value.priority}
          onChange={(e) => update({ priority: e.target.value as CasePriority | '' })}
        >
          <option value="">All priorities</option>
          {CASE_PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {CASE_PRIORITY_LABELS[priority]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="case-sort" className="mb-1 block text-sm font-medium text-gray-700">
          Sort
        </label>
        <select
          id="case-sort"
          className={inputClass}
          value={`${value.sort_by}:${value.sort_order}`}
          onChange={(e) => {
            const [sort_by, sort_order] = e.target.value.split(':');
            update({ sort_by, sort_order: sort_order as 'asc' | 'desc' });
          }}
        >
          <option value="created_at:desc">Newest first</option>
          <option value="created_at:asc">Oldest first</option>
          <option value="title:asc">Title A–Z</option>
          <option value="priority:desc">Priority high–low</option>
        </select>
      </div>
    </div>
  );
}
