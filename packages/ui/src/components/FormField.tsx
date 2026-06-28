import type { ReactNode } from 'react';

import { cn } from '../lib/cn';
import { Label } from './Label';

export interface FormFieldProps {
  label: string;
  htmlFor: string;
  children: ReactNode;
  error?: string;
  hint?: string;
  required?: boolean;
  className?: string;
}

export function FormField({
  label,
  htmlFor,
  children,
  error,
  hint,
  required,
  className,
}: FormFieldProps) {
  const errorId = error ? `${htmlFor}-error` : undefined;
  const hintId = hint ? `${htmlFor}-hint` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined;

  return (
    <div className={cn('space-y-1', className)}>
      <Label htmlFor={htmlFor} required={required}>
        {label}
      </Label>
      <div aria-describedby={describedBy}>{children}</div>
      {hint && !error ? (
        <p id={hintId} className="text-xs text-gray-500">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
