import type { Metadata } from 'next';
import { createMetadata } from '@/lib/seo';

export const metadata: Metadata = createMetadata({
  title: 'LO Leave-Behind — Print',
  description: 'Printable Mortgage Readiness Partnership leave-behind for loan officers.',
  path: '/resources/partner-kit/print/leave-behind',
});

export default function LeaveBehindLayout({ children }: { children: React.ReactNode }) {
  return children;
}
