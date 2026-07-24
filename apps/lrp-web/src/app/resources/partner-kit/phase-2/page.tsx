import Link from 'next/link';
import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Premium Partner Sales Kit — Phase 2',
  description:
    'Lender-grade Mortgage Readiness Solutions package: guide, deck outline, referral form, welcome packet, drips, and 90-day campaign.',
  path: '/resources/partner-kit/phase-2',
});

const items = [
  {
    title: 'Partnership Guide',
    href: '/resources/partner-kit/guide',
    body: '20-page manuscript for designed PDF — institutional narrative for bank and lender meetings.',
  },
  {
    title: 'Lender meeting deck',
    href: '/resources/partner-kit/phase-2#deck',
    body: 'Slide-by-slide outline with speaker notes for PowerPoint production.',
  },
  {
    title: 'Fillable referral form',
    href: '/resources/partner-kit/referral',
    body: 'Digital form with print stylesheet — partner consent and minimal PII.',
  },
  {
    title: 'Leave-behind print sheet',
    href: '/resources/partner-kit/print/leave-behind',
    body: 'Print-optimized summary for LO folder inserts and QR to the full kit.',
  },
  {
    title: 'Welcome packet & Canva specs',
    href: '/resources/partner-kit/phase-2#packet',
    body: 'Onboarding insert order and Brand Kit template IDs for designers.',
  },
  {
    title: '90-day campaign',
    href: '/resources/partner-kit/phase-2#campaign',
    body: 'Soft launch → design partners → public narrative calendar.',
  },
];

export default function PartnerKitPhase2Page() {
  return (
    <>
      <PageHero
        eyebrow="Phase 2"
        title="Premium Mortgage Partner Sales Kit"
        description="Elevate from credit-repair aesthetics to Mortgage Readiness Solutions collateral lenders trust as an extension of their team."
        tone="sand"
        actions={
          <>
            <Button href="/resources/partner-kit/phase-3" variant="primary" size="lg">
              Phase 3 print kit
            </Button>
            <Button href="/resources/partner-kit/guide" variant="secondary" size="lg">
              Open partnership guide
            </Button>
          </>
        }
      />

      <Section tone="white">
        <p className="max-w-3xl text-sm text-ink-700">{ADVISORY_DISCLAIMER_SHORT}</p>
        <div className="mt-8">
          <SectionHeading
            title="What’s included"
            description="Canonical manuscripts live in Vol 07. Designed PDF/PPT/Canva binaries are produced from these specs."
          />
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <article
              key={item.title}
              className="flex h-full flex-col rounded-lg border border-navy-900/10 bg-sand-50 p-6"
            >
              <h2 className="font-display text-xl text-navy-900">{item.title}</h2>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700">{item.body}</p>
              <Link
                href={item.href}
                className="mt-4 text-sm font-medium text-teal-700 hover:underline"
              >
                Open →
              </Link>
            </article>
          ))}
        </div>

        <div
          id="deck"
          className="mt-16 scroll-mt-24 rounded-lg border border-navy-900/10 bg-white p-6"
        >
          <h2 className="font-display text-2xl text-navy-900">Lender meeting deck</h2>
          <p className="mt-3 text-sm text-ink-700">
            12–13 slides: problem, partnership model, advisory readiness, visibility, compliance,
            onboarding, what we never claim, next step. Full outline with speaker notes is in the
            Build Bible Phase 2 kit for export to PowerPoint.
          </p>
        </div>

        <div
          id="packet"
          className="mt-8 scroll-mt-24 rounded-lg border border-navy-900/10 bg-white p-6"
        >
          <h2 className="font-display text-2xl text-navy-900">Welcome packet & Canva</h2>
          <p className="mt-3 text-sm text-ink-700">
            Welcome packet insert order, portal onboarding concept (co-brand + claim
            acknowledgment), and Canva template IDs C-01–C-10 are documented for design production.
          </p>
        </div>

        <div
          id="campaign"
          className="mt-8 scroll-mt-24 rounded-lg border border-navy-900/10 bg-white p-6"
        >
          <h2 className="font-display text-2xl text-navy-900">90-day campaign</h2>
          <p className="mt-3 text-sm text-ink-700">
            Days 1–30 soft launch, 31–60 design partners, 61–90 public narrative—with LinkedIn,
            email, flyers, and webinars. No guaranteed-mortgage paid creatives.
          </p>
        </div>

        <p className="mt-10 text-sm">
          <Link href="/resources/partner-kit" className="font-medium text-teal-700 hover:underline">
            ← Phase 1 kit hub
          </Link>
        </p>
      </Section>

      <CtaBand
        title="Brief a lender with the premium kit."
        description="Walk production and compliance through the guide, deck, and referral path."
        primaryHref="/contact?intent=lender"
        primaryLabel="Book a briefing"
        secondaryHref="/lenders"
        secondaryLabel="Lender landing"
      />
    </>
  );
}
