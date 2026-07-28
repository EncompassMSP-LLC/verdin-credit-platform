'use client';

import type { ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import { RealtorAuthProvider } from '@/lib/realtor/auth';

export function RealtorProviders({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <RealtorAuthProvider>{children}</RealtorAuthProvider>
    </ThemeProvider>
  );
}
