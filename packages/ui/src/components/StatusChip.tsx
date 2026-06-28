import type { HTMLAttributes, ReactNode } from 'react';

import { cn } from '../lib/cn';

export type StatusChipVariant = 'neutral' | 'success' | 'warning' | 'danger' | 'info';

export interface StatusChipProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: StatusChipVariant;
  children: ReactNode;
  dot?: boolean;
}

const chipVariants: Record<StatusChipVariant, { container: string; dot: string }> = {
  neutral: { container: 'bg-gray-100 text-gray-700', dot: 'bg-gray-500' },
  success: { container: 'bg-green-50 text-green-700', dot: 'bg-green-500' },
  warning: { container: 'bg-yellow-50 text-yellow-800', dot: 'bg-yellow-500' },
  danger: { container: 'bg-red-50 text-red-700', dot: 'bg-red-500' },
  info: { container: 'bg-blue-50 text-blue-700', dot: 'bg-blue-500' },
};

export function StatusChip({
  variant = 'neutral',
  dot = true,
  className,
  children,
  ...props
}: StatusChipProps) {
  const styles = chipVariants[variant];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        styles.container,
        className,
      )}
      {...props}
    >
      {dot ? (
        <span className={cn('h-1.5 w-1.5 shrink-0 rounded-full', styles.dot)} aria-hidden="true" />
      ) : null}
      {children}
    </span>
  );
}
