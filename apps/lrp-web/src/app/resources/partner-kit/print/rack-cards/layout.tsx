import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Rack Cards — Print',
  description: 'Printable 4×9 rack cards for lenders, realtors, and borrowers.',
  path: '/resources/partner-kit/print/rack-cards',
});

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}
