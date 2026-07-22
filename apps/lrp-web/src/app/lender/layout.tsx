import type { ReactNode } from 'react';
import { LenderProviders } from '@/components/providers/LenderProviders';

export default function LenderRootLayout({ children }: { children: ReactNode }) {
  return <LenderProviders>{children}</LenderProviders>;
}
