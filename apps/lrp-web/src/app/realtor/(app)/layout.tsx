import type { ReactNode } from 'react';
import { RealtorShell } from '@/components/realtor/RealtorShell';

export default function RealtorAppLayout({ children }: { children: ReactNode }) {
  return <RealtorShell>{children}</RealtorShell>;
}
