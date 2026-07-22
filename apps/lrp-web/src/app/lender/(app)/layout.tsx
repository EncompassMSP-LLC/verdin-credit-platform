import type { ReactNode } from 'react';
import { LenderShell } from '@/components/lender/LenderShell';

export default function LenderAppLayout({ children }: { children: ReactNode }) {
  return <LenderShell>{children}</LenderShell>;
}
