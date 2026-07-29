import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Partners Hub — Choose Your Audience',
  description:
    'Lending Readiness Partners audience landings for lenders, realtors, builders, attorneys, advisors, and operators.',
  path: '/partners',
});

const audiences = [
  {
    href: '/lenders',
    title: 'Lenders',
    body: 'Mortgage partners who need advisory readiness visibility without approval theater.',
  },
  {
    href: '/realtors',
    title: 'Realtors',
    body: 'Keep buyers engaged when financing needs more time—with claim-safe stage language.',
  },
  {
    href: '/builders',
    title: 'Builders',
    body: 'Prepare community buyers for the financing conversation alongside preferred lenders.',
  },
  {
    href: '/attorneys',
    title: 'Attorneys',
    body: 'Readiness support that stays in its lane—separate from legal advice and underwriting.',
  },
  {
    href: '/advisors',
    title: 'Advisors',
    body: 'Financial planners and insurance professionals coordinating home goals ethically.',
  },
  {
    href: '/borrowers',
    title: 'Borrowers',
    body: 'A dignified plan for “not yet”—guided through trusted lenders and operators.',
  },
];

export default function PartnersPage() {
  return (
    <>
      <PageHero
        eyebrow="Partners hub"
        title="Choose the partnership path that fits your role."
        description="Lending Readiness Partners helps more borrowers become lending ready—through lenders, operators, and allied professionals. Advisory only; never a guarantee of approval or funding."
        actions={
          <>
            <Button href="/contact?intent=partner" variant="inverse" size="lg">
              Talk with partnerships
            </Button>
            <Button
              href="/resources/partner-kit"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Open partner kit
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Audiences"
          title="One brand. Clear lanes for every partner."
          description="Pick your landing—each page stays claim-safe and compliance-minded."
        />
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {audiences.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="block rounded-lg bg-sand-100 p-6 ring-1 ring-navy-900/5 transition hover:ring-navy-900/20"
            >
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
              <span className="mt-4 inline-block text-sm font-medium text-teal-800">
                View landing →
              </span>
            </a>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          title="Operators"
          description="Credit services firms productizing mortgage readiness for lender and realtor channels."
        />
        <div className="mt-8">
          <Button href="/crm/login" variant="secondary">
            Open enterprise CRM
          </Button>
        </div>
      </Section>

      <CtaBand
        title="Become the readiness partner lenders prefer."
        description="We’ll help you package operations into partner-ready signals and a pilot your compliance team can defend."
        primaryHref="/contact?intent=operator"
        primaryLabel="Talk with partnerships"
      />
    </>
  );
}
