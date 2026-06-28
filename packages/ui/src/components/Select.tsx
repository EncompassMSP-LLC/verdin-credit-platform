import { forwardRef, type ReactNode, type SelectHTMLAttributes } from 'react';

import { cn } from '../lib/cn';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  hasError?: boolean;
  placeholder?: string;
  children: ReactNode;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className, hasError, placeholder, children, ...props },
  ref,
) {
  return (
    <select
      ref={ref}
      className={cn(
        'block w-full rounded-md border bg-white px-3 py-2 text-gray-900 shadow-sm transition-colors',
        'focus:outline-none focus:ring-1',
        hasError
          ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
          : 'border-gray-300 focus:border-brand-500 focus:ring-brand-500',
        'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
        className,
      )}
      aria-invalid={hasError || undefined}
      {...props}
    >
      {placeholder ? (
        <option value="" disabled>
          {placeholder}
        </option>
      ) : null}
      {children}
    </select>
  );
});
