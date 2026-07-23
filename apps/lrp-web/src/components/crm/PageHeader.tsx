import type { ReactNode } from 'react';

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow ? (
          <p className="text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-gold-600 dark:text-gold-400">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-navy-900 dark:text-white">
          {title}
        </h1>
        {description ? (
          <p className="mt-1.5 max-w-2xl text-sm text-slate-600 dark:text-white/65">
            {description}
          </p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </header>
  );
}
