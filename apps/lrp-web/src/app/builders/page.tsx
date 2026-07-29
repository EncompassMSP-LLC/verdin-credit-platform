import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Builders — Preparing Buyers for Financing',
  description:
    'Help community buyers organize credit and documentation habits while preferred lenders stay informed—with Lending Readiness Partners.',
  path: '/builders',
});

export default function BuildersPage() {
  return (
    <>
      <PageHero
        eyebrow="Builder partnership"
        title="Preparing buyers for the financing conversation."
        description="Help community buyers organize credit and documentation habits—while your preferred lenders stay informed. Advisory readiness only—never an approval promise."
        actions={
          <>
            <Button href="/contact?intent=builder" variant="inverse" size="lg">
              Partner briefing
            </Button>
            <Button
              href="/contact?intent=builder"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Contact partnerships
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Why builders partner"
          title="Sales offices need claim-safe language when financing takes longer."
          description={ADVISORY_DISCLAIMER_SHORT}
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'Keep buyers in motion',
              body: 'When a buyer is “not yet,” give them a dignified plan instead of silence that kills the contract.',
            },
            {
              title: 'Preferred-lender alignment',
              body: 'Refer through lenders and operators who already underwrite—so readiness never pretends to be approval.',
            },
            {
              title: 'Sales-office scripts',
              body: 'Equip teams with claim-safe talking points from the Partner Kit—no score guarantees, no funding promises.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-lg bg-sand-100 p-6">
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          title="Referral flow"
          description="Builders typically introduce buyers through preferred lenders and credit operators—not as a standalone credit service."
        />
        <ol className="mt-10 space-y-4">
          {[
            'Refer → introduce the buyer to a preferred lender or readiness operator.',
            'Plan → staff create an advisory readiness plan with clear next steps.',
            'Update → partners receive progress language sales offices can explain.',
            'Return → buyer re-enters the financing conversation when the file is organized.',
          ].map((step, index) => (
            <li key={step} className="flex gap-4 rounded-lg bg-white p-5 ring-1 ring-navy-900/8">
              <span className="font-mono text-sm font-semibold text-gold-700">
                {String(index + 1).padStart(2, '0')}
              </span>
              <p className="text-sm text-ink-700 sm:text-base">{step}</p>
            </li>
          ))}
        </ol>
      </Section>

      <Section tone="white">
        <SectionHeading title="Claim-safe language for sales offices" />
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <article className="rounded-lg border border-teal-700/20 bg-teal-700/5 p-6">
            <h3 className="font-display text-xl text-navy-900">Say</h3>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-ink-700">
              <li>We can connect you with a readiness partner and preferred lender.</li>
              <li>Readiness is advisory—your lender still underwrites the loan.</li>
              <li>Progress updates help everyone set honest expectations.</li>
            </ul>
          </article>
          <article className="rounded-lg border border-red-700/20 bg-red-700/5 p-6">
            <h3 className="font-display text-xl text-navy-900">Never say</h3>
            <ul className="mt-3 list-disc space-y-2 pl-5 text-sm text-ink-700">
              <li>We will get you approved or funded.</li>
              <li>We guarantee a score increase or closing date.</li>
              <li>This replaces underwriting or legal advice.</li>
            </ul>
          </article>
        </div>
      </Section>

      <Section>
        <SectionHeading title="FAQ" />
        <dl className="mt-8 space-y-6">
          {[
            {
              q: 'Do builders underwrite through LRP?',
              a: 'No. Lenders underwrite. LRP helps organize advisory readiness and partner communication.',
            },
            {
              q: 'Can sales quote a readiness score as approval?',
              a: 'Never. Lending Readiness Score™ is advisory only and not a CRA credit score or underwriting decision.',
            },
          ].map((item) => (
            <div key={item.q} className="rounded-lg bg-white p-5 ring-1 ring-navy-900/8">
              <dt className="font-medium text-navy-900">{item.q}</dt>
              <dd className="mt-2 text-sm text-ink-700">{item.a}</dd>
            </div>
          ))}
        </dl>
      </Section>

      <CtaBand
        title="Brief your preferred lenders on a readiness standard."
        description="Partner briefings keep builders, lenders, and operators aligned—without approval theater."
        primaryHref="/contact?intent=builder"
        primaryLabel="Request a partner briefing"
        secondaryHref="/resources/partner-kit"
        secondaryLabel="Open partner kit"
      />
    </>
  );
}
