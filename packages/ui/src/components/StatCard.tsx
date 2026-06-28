import type { ReactNode } from 'react';

import { cn } from '../lib/cn';
import { Card, CardContent } from './Card';

export interface StatCardProps {
  label: string;
  value: ReactNode;
  description?: string;
  className?: string;
  valueClassName?: string;
}

export function StatCard({ label, value, description, className, valueClassName }: StatCardProps) {
  return (
    <Card className={className}>
      <CardContent>
        <p className="text-sm text-gray-500">{label}</p>
        <p className={cn('mt-1 text-3xl font-bold text-gray-900', valueClassName)}>{value}</p>
        {description ? <p className="mt-1 text-xs text-gray-400">{description}</p> : null}
      </CardContent>
    </Card>
  );
}
