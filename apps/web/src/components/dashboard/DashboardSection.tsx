import type { ReactNode } from 'react';

interface DashboardSectionProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function DashboardSection({ title, description, children }: DashboardSectionProps) {
  return (
    <section>
      <div className="mb-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">{title}</h2>
        {description ? <p className="mt-1 text-sm text-gray-500">{description}</p> : null}
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-5">{children}</div>
    </section>
  );
}
