import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Borrower Readiness Guide — Print',
  description: 'Printable Mortgage Readiness Guide for borrowers.',
  path: '/resources/partner-kit/print/borrower-guide',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
