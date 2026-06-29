export interface DocumentFiltersValue {
  search: string;
  case_id: string;
  is_duplicate: '' | 'true';
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

interface DocumentFiltersProps {
  value: DocumentFiltersValue;
  onChange: (value: DocumentFiltersValue) => void;
}

const inputClass =
  'block w-full rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500';

export function DocumentFilters({ value, onChange }: DocumentFiltersProps) {
  const update = (patch: Partial<DocumentFiltersValue>) => onChange({ ...value, ...patch });

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
      <div className="lg:col-span-2">
        <label htmlFor="doc-search" className="mb-1 block text-sm font-medium text-gray-700">
          Search
        </label>
        <input
          id="doc-search"
          type="search"
          placeholder="Title, file name..."
          className={inputClass}
          value={value.search}
          onChange={(e) => update({ search: e.target.value })}
        />
      </div>
      <div>
        <label htmlFor="doc-duplicate" className="mb-1 block text-sm font-medium text-gray-700">
          Duplicate filter
        </label>
        <select
          id="doc-duplicate"
          className={inputClass}
          value={value.is_duplicate}
          onChange={(e) => update({ is_duplicate: e.target.value as '' | 'true' })}
        >
          <option value="">All documents</option>
          <option value="true">Duplicates only</option>
        </select>
      </div>
      <div>
        <label htmlFor="doc-sort" className="mb-1 block text-sm font-medium text-gray-700">
          Sort
        </label>
        <select
          id="doc-sort"
          className={inputClass}
          value={`${value.sort_by}:${value.sort_order}`}
          onChange={(e) => {
            const [sort_by, sort_order] = e.target.value.split(':');
            update({ sort_by, sort_order: sort_order as 'asc' | 'desc' });
          }}
        >
          <option value="created_at:desc">Newest first</option>
          <option value="title:asc">Title A–Z</option>
          <option value="file_size:desc">Largest first</option>
        </select>
      </div>
    </div>
  );
}
