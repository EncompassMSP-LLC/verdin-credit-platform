import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Attorneys — Readiness Support in Its Lane',
  description:
    'Advisory education and documentation habits for clients with financing goals—separate from legal advice and underwriting.',
  path: '/attorneys',
});

export default function AttorneysPage() {
  return (
    <>
      <PageHero
        eyebrow="Attorney partnership"
        title="Readiness support that stays in its lane."
        description="Advisory education and documentation habits for clients with financing goals—separate from legal advice and underwriting. We support readiness. Partners underwrite."
        actions={
          <>
            <Button href="/contact?intent=attorney" variant="inverse" size="lg">
              Partner briefing
            </Button>
            <Button
              href="/contact?intent=attorney"
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
          eyebrow="Boundary of services"
          title="Legal counsel remains yours. Readiness remains advisory."
          description={ADVISORY_DISCLAIMER_SHORT}
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'What we do',
              body: 'Help clients organize credit documentation and dispute workflows through staff-mediated operators—never unsupervised filing.',
            },
            {
              title: 'What we do not do',
              body: 'We do not practice law, provide legal opinions, or replace attorney representation in disputes or closings.',
            },
            {
              title: 'How lenders stay separate',
              body: 'Underwriting, product eligibility, and funding decisions remain with the lender—always.',
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
          title="Referral path"
          description="Attorneys typically refer clients toward preferred lenders and credit operators who run Lending Readiness Partners workflows."
        />
        <ol className="mt-10 space-y-4">
          {[
            'Identify clients whose home-financing goals need more preparation.',
            'Introduce a preferred lender or readiness operator for advisory planning.',
            'Keep legal strategy independent while readiness work stays documented and mediated.',
            'Clients return to financing conversations when documentation habits support the next step.',
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
        <SectionHeading title="Privacy & professionalism" />
        <p className="mt-6 max-w-3xl text-sm leading-relaxed text-ink-700 sm:text-base">
          Client information stays within authorized partner and operator systems. Marketing and
          status language stay claim-safe: no guaranteed outcomes, no score-point promises, and no
          confusion between readiness education and legal advice.
        </p>
      </Section>

      <Section>
        <SectionHeading title="FAQ" />
        <dl className="mt-8 space-y-6">
          {[
            {
              q: 'Is this a substitute for legal counsel?',
              a: 'No. Lending Readiness Partners provides advisory readiness education and operator workflows—not legal advice.',
            },
            {
              q: 'Do you auto-file bureau disputes?',
              a: 'No. Dispute actions remain staff-mediated. The platform never unsupervised-files with bureaus.',
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
        title="Coordinate readiness without blurring professional lanes."
        description="Partner briefings clarify how attorneys, lenders, and operators collaborate ethically."
        primaryHref="/contact?intent=attorney"
        primaryLabel="Request a partner briefing"
        secondaryHref="/resources/partner-kit"
        secondaryLabel="Open partner kit"
      />
    </>
  );
}
