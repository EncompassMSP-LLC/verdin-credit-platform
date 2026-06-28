import { forwardRef, type InputHTMLAttributes } from 'react';

import { cn } from '../lib/cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  hasError?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, hasError, type = 'text', ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      type={type}
      className={cn(
        'block w-full rounded-md border px-3 py-2 text-gray-900 shadow-sm transition-colors',
        'placeholder:text-gray-400',
        'focus:outline-none focus:ring-1',
        hasError
          ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
          : 'border-gray-300 focus:border-brand-500 focus:ring-brand-500',
        'disabled:cursor-not-allowed disabled:bg-gray-50 disabled:text-gray-500',
        className,
      )}
      aria-invalid={hasError || undefined}
      {...props}
    />
  );
});
