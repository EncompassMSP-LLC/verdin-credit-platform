import Link from 'next/link';
import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Mortgage Partner Marketing Kit',
  description:
    'Claim-safe letters, brochure copy, flyers, checklists, and campaign outlines for Lending Readiness Partners mortgage partnerships.',
  path: '/resources/partner-kit',
});

const kitAssets = [
  {
    title: 'Cover letter',
    audience: 'Loan officers',
    description: 'Welcome letter for LO outreach—partnership framing without outcome guarantees.',
  },
  {
    title: 'Trifold brochure',
    audience: 'Print / Canva',
    description: 'Front, inside, process, and back copy blocks for institutional design.',
  },
  {
    title: 'Referral flyer',
    audience: 'Leave-behind',
    description: '“Not yet” flyer that keeps relationships attached to a clear next step.',
  },
  {
    title: 'LO one-pager',
    audience: 'Lenders',
    description: 'Benefits grid: specialist, portal, progress reports, white-glove service.',
  },
  {
    title: 'Readiness checklist',
    audience: 'LO + borrower',
    description: 'Advisory checklist for financing conversations—not underwriting.',
  },
  {
    title: 'Social & email campaigns',
    audience: 'Marketing',
    description: 'Five social posts and a five-email drip with claim-safe subjects and bodies.',
  },
  {
    title: 'LinkedIn themes',
    audience: 'BD',
    description: 'Message pillars and captions for professional outreach.',
  },
  {
    title: 'Realtor co-channel kit',
    audience: 'Realtors',
    description: 'Keep buyers engaged with shared readiness language and expectation scripts.',
  },
];

export default function PartnerKitPage() {
  return (
    <>
      <PageHero
        eyebrow="Partner kit"
        title="Mortgage Partner Marketing Kit"
        description="Lender-grade collateral for BD and partnerships. Helping More Borrowers Become Lending Ready.—without guarantee culture."
        tone="sand"
        actions={
          <>
            <Button href="/lenders" variant="primary" size="lg">
              Lender landing
            </Button>
            <Button href="/contact?intent=lender" variant="secondary" size="lg">
              Book a briefing
            </Button>
          </>
        }
      />

      <Section tone="white">
        <p className="max-w-3xl text-sm text-ink-700">{ADVISORY_DISCLAIMER_SHORT}</p>
        <div className="mt-8">
          <SectionHeading
            title="What’s in the kit"
            description="Canonical copy lives in the Build Bible (Vol 07). Use this hub to brief partners and request designed print files."
          />
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-2">
          {kitAssets.map((asset) => (
            <article
              key={asset.title}
              className="flex h-full flex-col rounded-lg border border-navy-900/10 bg-sand-50 p-6"
            >
              <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-700">
                {asset.audience}
              </p>
              <h2 className="mt-3 font-display text-2xl text-navy-900">{asset.title}</h2>
              <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700">
                {asset.description}
              </p>
            </article>
          ))}
        </div>
        <div className="mt-10 flex flex-wrap gap-4 text-sm">
          <Link href="/lenders" className="font-medium text-teal-700 hover:underline">
            View lender partnership page →
          </Link>
          <Link href="/realtors" className="font-medium text-teal-700 hover:underline">
            View realtor partnership page →
          </Link>
          <Link href="/resources" className="font-medium text-teal-700 hover:underline">
            All resources →
          </Link>
          <Link
            href="/contact?intent=lender&resource=partner-kit"
            className="font-medium text-teal-700 hover:underline"
          >
            Request designed print pack →
          </Link>
        </div>
      </Section>

      <CtaBand
        title="Ready to hand lenders a kit they’d be proud to share?"
        description="We’ll walk production and compliance through the partnership model and leave-behinds."
        primaryHref="/contact?intent=lender"
        primaryLabel="Schedule a briefing"
        secondaryHref="/lender/login"
        secondaryLabel="Lender workspace"
      />
    </>
  );
}
