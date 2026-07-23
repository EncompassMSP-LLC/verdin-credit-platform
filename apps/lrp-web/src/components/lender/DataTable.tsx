import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export type Column<T> = {
  key: string;
  header: string;
  className?: string;
  cell: (row: T) => ReactNode;
};

export function DataTable<T extends { id: string }>({
  columns,
  rows,
  empty = 'No records.',
  onRowClick,
}: {
  columns: Column<T>[];
  rows: T[];
  empty?: string;
  onRowClick?: (row: T) => void;
}) {
  if (!rows.length) {
    return <p className="px-1 py-8 text-center text-sm text-slate-500">{empty}</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={cn(
                  'sticky top-0 border-b border-navy-900/10 bg-[#F8FAFC] px-3 py-2.5 text-[0.65rem] font-semibold uppercase tracking-wider text-slate-500 dark:border-white/10 dark:bg-navy-900/60 dark:text-white/50',
                  col.className,
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr
              key={row.id}
              className={cn(
                'border-b border-navy-900/8 dark:border-white/8',
                onRowClick && 'cursor-pointer hover:bg-navy-900/[0.03] dark:hover:bg-white/[0.03]',
              )}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
            >
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={cn(
                    'border-b border-navy-900/8 px-3 py-3 align-middle dark:border-white/8',
                    col.className,
                  )}
                >
                  {col.cell(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
