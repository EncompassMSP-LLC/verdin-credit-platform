import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function PortalCard({
  children,
  className,
  title,
  action,
  description,
}: {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <section
      className={cn(
        'rounded-brand border border-navy-900/10 bg-white p-5 shadow-soft dark:border-white/10 dark:bg-navy-800/80',
        className,
      )}
    >
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title ? (
              <h2 className="text-sm font-semibold uppercase tracking-wider text-navy-900 dark:text-white">
                {title}
              </h2>
            ) : null}
            {description ? (
              <p className="mt-1 text-sm text-slate-500 dark:text-white/60">{description}</p>
            ) : null}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function StatTile({
  label,
  value,
  hint,
  tone = 'default',
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: 'default' | 'good' | 'warn';
}) {
  return (
    <div className="rounded-brand border border-navy-900/10 bg-sand-50 p-4 dark:border-white/10 dark:bg-navy-900/50">
      <p className="text-[0.65rem] font-medium uppercase tracking-eyebrow text-slate-500 dark:text-white/50">
        {label}
      </p>
      <p
        className={cn(
          'mt-2 text-2xl font-semibold tabular-nums',
          tone === 'good' && 'text-emerald-600 dark:text-emerald-500',
          tone === 'warn' && 'text-warning',
          tone === 'default' && 'text-navy-900 dark:text-white',
        )}
      >
        {value}
      </p>
      {hint ? <p className="mt-1 text-xs text-slate-500 dark:text-white/55">{hint}</p> : null}
    </div>
  );
}

export function StatusPill({
  children,
  tone = 'neutral',
}: {
  children: ReactNode;
  tone?: 'neutral' | 'good' | 'warn' | 'info';
}) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full px-2.5 py-0.5 text-[0.65rem] font-semibold uppercase tracking-wide',
        tone === 'neutral' && 'bg-sand-200 text-navy-900 dark:bg-white/10 dark:text-white',
        tone === 'good' && 'bg-emerald-600/15 text-emerald-700 dark:text-emerald-400',
        tone === 'warn' && 'bg-warning/15 text-warning',
        tone === 'info' && 'bg-gold-500/15 text-gold-700 dark:text-gold-400',
      )}
    >
      {children}
    </span>
  );
}
