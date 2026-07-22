import { Suspense } from 'react';
import { ContactForm } from '@/components/forms/ContactForm';
import { PageHero } from '@/components/sections/PageHero';
import { Container } from '@/components/ui/Container';
import { siteConfig } from '@/lib/site';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Contact',
  description:
    'Book a Lending Readiness Partners briefing for lenders, operators, realtor programs, or enterprise networks.',
  path: '/contact',
});

export default function ContactPage() {
  return (
    <>
      <PageHero
        eyebrow="Contact"
        title="Let’s talk readiness."
        description="Tell us about your channel, volume, and fallout challenges. We’ll follow up with a briefing tailored to lenders, operators, or realty partners."
      />
      <Container className="grid gap-12 py-16 lg:grid-cols-[0.9fr_1.1fr] lg:gap-16 lg:py-20">
        <aside className="space-y-6">
          <div>
            <h2 className="font-display text-2xl text-navy-900">Briefing desk</h2>
            <p className="mt-3 text-ink-700">
              Most teams include production, operations, and compliance in the first conversation so
              pilot scope stays realistic.
            </p>
          </div>
          <dl className="space-y-4 text-sm">
            <div>
              <dt className="font-medium text-navy-900">Email</dt>
              <dd className="mt-1">
                <a className="text-teal-700 underline" href={`mailto:${siteConfig.email}`}>
                  {siteConfig.email}
                </a>
              </dd>
            </div>
            <div>
              <dt className="font-medium text-navy-900">Phone</dt>
              <dd className="mt-1 text-ink-700">{siteConfig.phone}</dd>
            </div>
            <div>
              <dt className="font-medium text-navy-900">Office</dt>
              <dd className="mt-1 text-ink-700">
                {siteConfig.address.line1}
                <br />
                {siteConfig.address.city}, {siteConfig.address.state} {siteConfig.address.postal}
              </dd>
            </div>
          </dl>
        </aside>
        <div className="rounded-lg bg-white p-6 shadow-soft ring-1 ring-navy-900/8 sm:p-8">
          <Suspense fallback={<p className="text-ink-700">Loading form…</p>}>
            <ContactForm />
          </Suspense>
        </div>
      </Container>
    </>
  );
}
