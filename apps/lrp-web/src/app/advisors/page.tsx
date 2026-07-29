import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Advisors — When Home Goals Need Preparation',
  description:
    'Coordinate with lenders through an advisory readiness partner—visibility without confusing your financial advice.',
  path: '/advisors',
});

export default function AdvisorsPage() {
  return (
    <>
      <PageHero
        eyebrow="Advisor partnership"
        title="When clients’ home goals need more preparation."
        description="Coordinate with lenders through an advisory readiness partner—visibility without confusing your advice. We support readiness. Lenders underwrite."
        actions={
          <>
            <Button href="/contact?intent=advisor" variant="inverse" size="lg">
              Partner briefing
            </Button>
            <Button
              href="/contact?intent=advisor"
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
          eyebrow="Who we serve"
          title="Financial planners, insurance professionals, and trusted advisors."
          description={ADVISORY_DISCLAIMER_SHORT}
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'Keep advice distinct',
              body: 'Your planning and product advice stay yours. Readiness education is a separate, claim-safe companion path.',
            },
            {
              title: 'Lender-visible progress',
              body: 'Preferred lenders can follow advisory stages without treating readiness as an approval decision.',
            },
            {
              title: 'Dignity-first handoffs',
              body: 'Help clients who are “not yet” for a mortgage conversation stay engaged with a clear next plan.',
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
        <SectionHeading title="How referrals work" />
        <ol className="mt-10 space-y-4">
          {[
            'Identify clients whose home goals need credit or documentation preparation.',
            'Introduce a preferred lender or readiness operator for an advisory plan.',
            'Stay informed through partner-safe progress language—not underwriting theater.',
            'Clients return to the financing conversation when the file is organized.',
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
        <SectionHeading title="What we never claim" />
        <ul className="mt-8 space-y-3 text-ink-700">
          {[
            'No guaranteed loan approval, pricing, or funding.',
            'No promised FICO point increases or “fix credit fast” outcomes.',
            'No unsupervised bureau filing or automatic dispute transmission.',
            'No replacement for licensed financial, insurance, or legal advice.',
          ].map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-teal-600" aria-hidden />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section>
        <SectionHeading title="FAQ" />
        <dl className="mt-8 space-y-6">
          {[
            {
              q: 'Will this conflict with my advice to clients?',
              a: 'No. Readiness work is advisory credit and documentation organization—distinct from your planning recommendations.',
            },
            {
              q: 'Is Lending Readiness Score™ a credit score?',
              a: 'No. It is an advisory readiness signal, not a CRA credit score and not an underwriting decision.',
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
        title="Coordinate home goals without confusing your advice."
        description="Partner briefings show how advisors, lenders, and operators stay in their lanes."
        primaryHref="/contact?intent=advisor"
        primaryLabel="Request a partner briefing"
        secondaryHref="/resources/partner-kit"
        secondaryLabel="Open partner kit"
      />
    </>
  );
}
