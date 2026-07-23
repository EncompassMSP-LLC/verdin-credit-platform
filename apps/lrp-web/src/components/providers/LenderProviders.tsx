'use client';

import type { ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { LenderAuthProvider } from '@/lib/lender/auth';

export function LenderProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <LenderAuthProvider>{children}</LenderAuthProvider>
    </ThemeProvider>
  );
}
