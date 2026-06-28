import { type LabelHTMLAttributes, type ReactNode } from 'react';

import { cn } from '../lib/cn';

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  children: ReactNode;
  required?: boolean;
}

export function Label({ className, children, required, ...props }: LabelProps) {
  return (
    <label className={cn('block text-sm font-medium text-gray-700', className)} {...props}>
      {children}
      {required ? (
        <span className="ml-0.5 text-red-600" aria-hidden="true">
          *
        </span>
      ) : null}
      {required ? <span className="sr-only"> (required)</span> : null}
    </label>
  );
}
