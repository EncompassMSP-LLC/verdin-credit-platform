import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Marketing Flyers — Print',
  description: 'Five printable Mortgage Readiness Partnership flyers.',
  path: '/resources/partner-kit/print/flyers',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
