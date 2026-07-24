import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Mortgage Partnership Guide — Print',
  description: 'Printable Mortgage Partnership Guide leave-behind.',
  path: '/resources/partner-kit/print/partnership-guide',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
