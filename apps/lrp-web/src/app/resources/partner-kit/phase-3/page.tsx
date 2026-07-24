import Link from 'next/link';
import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Phase 3 Partner Program — Print & Digital Kit',
  description:
    'Printable Mortgage Readiness Partner Program collateral: folder, welcome packet, brochures, guides, flyers, rack cards, and sales playbooks.',
  path: '/resources/partner-kit/phase-3',
});

const products = [
  {
    title: 'LO Quick Reference',
    href: '/resources/partner-kit/print/lo-quick-reference',
    body: 'One-page cheat sheet — referral workflow, timelines, readiness checklist. Print or PDF.',
    tag: 'Print',
  },
  {
    title: 'Sales Presentation Folder',
    href: '/resources/partner-kit/print/sales-folder',
    body: 'Front/back folder artwork with pocket insert order and QR targets.',
    tag: 'Print',
  },
  {
    title: 'Welcome Packet',
    href: '/resources/partner-kit/print/welcome-packet',
    body: 'Multi-page onboarding packet for newly signed partnerships.',
    tag: 'Print / PDF',
  },
  {
    title: 'Company Brochure',
    href: '/resources/partner-kit/print/brochure',
    body: 'Digital tri-fold brochure panels ready to print or hand to design.',
    tag: 'Print / PDF',
  },
  {
    title: 'Partnership Guide',
    href: '/resources/partner-kit/print/partnership-guide',
    body: 'Full leave-behind guide (readable + print) for lender meetings.',
    tag: 'Print / PDF',
  },
  {
    title: 'Borrower Readiness Guide',
    href: '/resources/partner-kit/print/borrower-guide',
    body: 'Educational booklet chapters for borrowers preparing for financing conversations.',
    tag: 'Print / PDF',
  },
  {
    title: 'Marketing Flyers (5)',
    href: '/resources/partner-kit/print/flyers',
    body: 'Didn’t Qualify, Mortgage Ready focus, Credit Holding You Back, Homeownership, Partner With Us.',
    tag: 'Print',
  },
  {
    title: 'Rack Cards (3)',
    href: '/resources/partner-kit/print/rack-cards',
    body: '4×9 lender, realtor, and borrower versions for office displays.',
    tag: 'Print',
  },
  {
    title: 'Sales Scripts & Objections',
    href: '/resources/partner-kit/print/sales-playbook',
    body: 'Cold call, voicemail, elevator, discovery, and objection responses.',
    tag: 'Print / PDF',
  },
  {
    title: 'Partner Presentation',
    href: '/resources/partner-kit/print/presentation',
    body: '~25-slide HTML deck — present in browser or print to PDF.',
    tag: 'Deck',
  },
  {
    title: 'Referral Form',
    href: '/resources/partner-kit/referral',
    body: 'Fillable digital referral form (Phase 2).',
    tag: 'Interactive',
  },
  {
    title: 'Classic leave-behind',
    href: '/resources/partner-kit/print/leave-behind',
    body: 'Phase 2 one-sheet leave-behind.',
    tag: 'Print',
  },
];

export default function PartnerKitPhase3Page() {
  return (
    <>
      <PageHero
        eyebrow="Phase 3 — End products"
        title="Mortgage Readiness Partner Program"
        description="Browser-ready collateral you can print or save as PDF today. Built from the Phase 3 manuscripts—claim-safe and brand-locked."
        tone="sand"
        actions={
          <>
            <Button
              href="/resources/partner-kit/print/lo-quick-reference"
              variant="primary"
              size="lg"
            >
              Print LO quick reference
            </Button>
            <Button
              href="/resources/partner-kit/print/partnership-guide"
              variant="secondary"
              size="lg"
            >
              Open partnership guide
            </Button>
          </>
        }
      />

      <Section tone="white">
        <p className="max-w-3xl text-sm text-ink-700">{ADVISORY_DISCLAIMER_SHORT}</p>
        <p className="mt-3 max-w-3xl text-sm text-ink-600">
          Use <strong>Print / Save as PDF</strong> on each piece (Chrome → Destination: Save as
          PDF). Press-ready die-cut folders and Canva binaries still come from design vendors; these
          pages are the production-ready digital pack.
        </p>
        <div className="mt-8">
          <SectionHeading
            title="Downloadable & printable products"
            description="Each link opens a designed layout with LRP branding, not a markdown file."
          />
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {products.map((item) => (
            <article
              key={item.href}
              className="flex flex-col rounded-brand border border-navy-900/10 bg-sand-50/60 p-6"
            >
              <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
                {item.tag}
              </p>
              <h3 className="mt-2 font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700">{item.body}</p>
              <Link
                href={item.href}
                className="mt-5 inline-flex text-sm font-semibold text-teal-700 hover:underline"
              >
                Open product →
              </Link>
            </article>
          ))}
        </div>
        <p className="mt-10 text-sm text-ink-600">
          Manuscripts (source of truth for designers):{' '}
          <code className="rounded bg-sand-100 px-1.5 py-0.5 text-xs">
            docs/.../partner-kit/phase-3/
          </code>
        </p>
      </Section>

      <CtaBand
        title="Ready for a lender briefing?"
        description="We’ll walk production through the partnership model with these leave-behinds."
        primaryHref="/contact?intent=lender&resource=phase-3-kit"
        primaryLabel="Book a briefing"
        secondaryHref="/lenders"
        secondaryLabel="Lender overview"
      />
    </>
  );
}
