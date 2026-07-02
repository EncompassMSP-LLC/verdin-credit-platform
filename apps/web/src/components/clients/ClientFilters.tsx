import { Button } from '@verdin/ui';
import type { ClientStatus } from '@verdin/api-client';

export interface ClientFiltersValue {
  search: string;
  status: ClientStatus | '';
  sort_by: 'created_at' | 'updated_at' | 'display_name' | 'status';
  sort_order: 'asc' | 'desc';
}

interface ClientFiltersProps {
  value: ClientFiltersValue;
  onChange: (value: ClientFiltersValue) => void;
}

const inputClass =
  'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function ClientFilters({ value, onChange }: ClientFiltersProps) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div>
        <label className="text-sm font-medium text-gray-700">Search</label>
        <input
          type="search"
          className={inputClass}
          placeholder="Name, email, phone…"
          value={value.search}
          onChange={(event) => onChange({ ...value, search: event.target.value })}
        />
      </div>
      <div>
        <label className="text-sm font-medium text-gray-700">Status</label>
        <select
          className={inputClass}
          value={value.status}
          onChange={(event) =>
            onChange({ ...value, status: event.target.value as ClientFiltersValue['status'] })
          }
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>
      <div>
        <label className="text-sm font-medium text-gray-700">Sort by</label>
        <select
          className={inputClass}
          value={value.sort_by}
          onChange={(event) =>
            onChange({
              ...value,
              sort_by: event.target.value as ClientFiltersValue['sort_by'],
            })
          }
        >
          <option value="created_at">Created</option>
          <option value="updated_at">Updated</option>
          <option value="display_name">Name</option>
          <option value="status">Status</option>
        </select>
      </div>
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <label className="text-sm font-medium text-gray-700">Order</label>
          <select
            className={inputClass}
            value={value.sort_order}
            onChange={(event) =>
              onChange({
                ...value,
                sort_order: event.target.value as ClientFiltersValue['sort_order'],
              })
            }
          >
            <option value="desc">Newest first</option>
            <option value="asc">Oldest first</option>
          </select>
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() =>
            onChange({
              search: '',
              status: '',
              sort_by: 'created_at',
              sort_order: 'desc',
            })
          }
        >
          Reset
        </Button>
      </div>
    </div>
  );
}
