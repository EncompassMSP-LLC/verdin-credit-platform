import { forwardRef, type TextareaHTMLAttributes } from 'react';

import { cn } from '../lib/cn';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  hasError?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, hasError, ...props },
  ref,
) {
  return (
    <textarea
      ref={ref}
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
