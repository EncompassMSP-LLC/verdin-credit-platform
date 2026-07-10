interface SortableTableHeaderProps {
  label: string;
  column: string;
  activeColumn: string;
  sortOrder: 'asc' | 'desc';
  onSort: (column: string) => void;
  align?: 'left' | 'right';
}

export function SortableTableHeader({
  label,
  column,
  activeColumn,
  sortOrder,
  onSort,
  align = 'left',
}: SortableTableHeaderProps) {
  const isActive = activeColumn === column;
  const indicator = isActive ? (sortOrder === 'asc' ? ' ↑' : ' ↓') : '';

  return (
    <th className={`px-4 py-3 font-medium ${align === 'right' ? 'text-right' : 'text-left'}`}>
      <button
        type="button"
        onClick={() => onSort(column)}
        className={`inline-flex items-center gap-1 hover:text-gray-900 ${
          isActive ? 'text-gray-900' : 'text-gray-500'
        } ${align === 'right' ? 'ml-auto' : ''}`}
      >
        {label}
        <span className="text-xs text-brand-600" aria-hidden="true">
          {indicator}
        </span>
      </button>
    </th>
  );
}
