import type { ReactNode } from 'react';

import { cn } from '../lib/cn';

export interface ErrorStateProps {
  title?: string;
  message: string;
  action?: ReactNode;
  className?: string;
}

export function ErrorState({
  title = 'Something went wrong',
  message,
  action,
  className,
}: ErrorStateProps) {
  return (
    <div
      className={cn('rounded-md border border-red-200 bg-red-50 px-4 py-3', className)}
      role="alert"
    >
      <h3 className="text-sm font-semibold text-red-800">{title}</h3>
      <p className="mt-1 text-sm text-red-700">{message}</p>
      {action ? <div className="mt-3">{action}</div> : null}
    </div>
  );
}
