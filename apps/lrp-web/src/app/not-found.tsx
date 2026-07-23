import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Container } from '@/components/ui/Container';

export default function NotFound() {
  return (
    <Container className="py-24 text-center">
      <p className="eyebrow">404</p>
      <h1 className="mt-3 font-display text-4xl text-navy-900">Page not found</h1>
      <p className="mx-auto mt-4 max-w-md text-ink-700">
        The page you’re looking for doesn’t exist or may have moved. Use the navigation or return
        home to continue.
      </p>
      <div className="mt-8 flex justify-center gap-3">
        <Button href="/" variant="primary">
          Go home
        </Button>
        <Button href="/contact" variant="secondary">
          Contact us
        </Button>
      </div>
      <p className="mt-6 text-sm">
        <Link href="/faqs" className="text-teal-700 hover:underline">
          Browse FAQs
        </Link>
      </p>
    </Container>
  );
}
