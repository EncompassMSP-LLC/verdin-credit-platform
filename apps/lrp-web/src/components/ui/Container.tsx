import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export function Container({
  children,
  className,
  as: Tag = 'div',
}: {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'section' | 'header' | 'footer' | 'nav' | 'main';
}) {
  return (
    <Tag className={cn('mx-auto w-full max-w-content px-5 sm:px-8', className)}>{children}</Tag>
  );
}
