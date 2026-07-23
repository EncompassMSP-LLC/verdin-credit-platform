import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Lenders — Mortgage Readiness Partnership',
  description:
    'Partner with Lending Readiness Partners to help more borrowers become lending ready—with advisory progress visibility, not approval theater.',
  path: '/lenders',
});

const processSteps = [
  'Borrower applies',
  'Credit or documentation gaps identified',
  'Referral sent',
  'Credit improvement & education plan',
  'Progress updates to partner',
  'Lending Ready (advisory)',
  'Return to loan officer',
];

const benefits = [
  {
    title: 'Dedicated mortgage specialist',
    body: 'Named partnership contact for mortgage-intent referrals and escalations.',
  },
  {
    title: 'Prompt initial review',
    body: 'Structured intake with clear next steps—so “not yet” has a plan.',
  },
  {
    title: 'Progress reports',
    body: 'Regular partner-visible status without turning readiness into underwriting.',
  },
  {
    title: 'Client portal',
    body: 'Borrowers complete tasks, upload documents, and learn in one place.',
  },
  {
    title: 'Lending readiness focus',
    body: 'Plans oriented to mortgage conversations—staff-mediated where required.',
  },
  {
    title: 'Rescore preparation support',
    body: 'Education and file organization when partners request a rescore path.',
  },
  {
    title: 'Flexible engagement',
    body: 'Partnership terms designed for trust—not pressure tactics.',
  },
  {
    title: 'White-glove partner service',
    body: 'Professional communication and SLA-minded updates for production teams.',
  },
];

const faqs = [
  {
    q: 'How long does readiness work take?',
    a: 'It varies by file complexity. We set expectations early and keep an agreed update cadence so production is never guessing.',
  },
  {
    q: 'How are updates provided?',
    a: 'Through the lender workspace, partnership digests, and the communication channel you agree during onboarding.',
  },
  {
    q: 'Can you help with FHA or Conventional paths?',
    a: 'We support education and documentation readiness. Product eligibility and underwriting always remain with the lender and applicable guidelines.',
  },
  {
    q: 'How does the referral process work?',
    a: 'Open a partnership referral, we accept and open a case plan, then you track advisory progress until the borrower is ready to return for the next financing conversation.',
  },
];

export default function LendersPage() {
  return (
    <>
      <PageHero
        eyebrow="Mortgage Readiness Partnership"
        title="Help more borrowers become lending ready."
        description="Turn “not yet” into a clear plan—while you stay informed. Lending Readiness Partners is an extension of your team for advisory readiness, education, and partner visibility—not a substitute for underwriting."
        actions={
          <>
            <Button href="/contact?intent=lender" variant="inverse" size="lg">
              Become a Mortgage Partner
            </Button>
            <Button href="/lender/login" variant="secondary" size="lg">
              Open lender workspace
            </Button>
            <Button
              href="/resources/partner-kit"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Partner marketing kit
            </Button>
          </>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="Why partners choose LRP"
          title="Institutional readiness support—without guarantee culture."
          description={ADVISORY_DISCLAIMER_SHORT}
        />
        <ul className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            'More borrowers prepared for the next lender conversation',
            'Clearer timelines and fewer status surprises',
            'Better borrower experience when today is “not yet”',
            'Stronger retention of relationships you already earned',
          ].map((item) => (
            <li
              key={item}
              className="flex gap-3 rounded-lg bg-sand-100 px-4 py-4 text-sm text-ink-700"
            >
              <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-gold-500" aria-hidden />
              {item}
            </li>
          ))}
        </ul>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Process"
          title="From referral to lending ready—then back to you."
          description="A controlled rhythm production teams can explain to borrowers and credit partners."
        />
        <ol className="mt-10 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {processSteps.map((step, index) => (
            <li
              key={step}
              className="rounded-lg border border-navy-900/10 bg-white p-4 text-sm text-ink-700"
            >
              <span className="font-mono text-xs font-semibold text-gold-700">
                {String(index + 1).padStart(2, '0')}
              </span>
              <p className="mt-2 font-medium text-navy-900">{step}</p>
            </li>
          ))}
        </ol>
      </Section>

      <Section tone="white">
        <SectionHeading
          eyebrow="Partner benefits"
          title="Built for loan officers and production teams."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {benefits.map((item) => (
            <article key={item.title} className="rounded-lg bg-sand-100 p-5">
              <h3 className="font-display text-lg text-navy-900">{item.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Readiness checklist"
          title="A conversation aid—not an underwriting decision."
          description="Share the Mortgage Readiness Checklist with LOs and borrowers to organize next steps."
        />
        <ul className="mt-8 grid gap-2 sm:grid-cols-2">
          {[
            'Stable income documentation in motion',
            'Utilization managed toward healthier ranges',
            'No new unexplained collections',
            'Inquiries understood and limited where appropriate',
            'Disputed items staff-reviewed when applicable',
            'Identity verified · documentation organized',
          ].map((item) => (
            <li key={item} className="flex gap-3 text-sm text-ink-700">
              <span className="text-gold-600" aria-hidden>
                ☐
              </span>
              {item}
            </li>
          ))}
        </ul>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button href="/resources/partner-kit" variant="primary">
            View full partner kit
          </Button>
          <Button href="/contact?intent=lender&resource=checklist" variant="secondary">
            Request printable checklist
          </Button>
        </div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="FAQ" title="Questions lenders ask first." />
        <dl className="mt-10 space-y-6">
          {faqs.map((item) => (
            <div key={item.q} className="rounded-lg border border-navy-900/10 bg-sand-50 p-5">
              <dt className="font-display text-lg text-navy-900">{item.q}</dt>
              <dd className="mt-2 text-sm leading-relaxed text-ink-700">{item.a}</dd>
            </div>
          ))}
        </dl>
      </Section>

      <Section>
        <div className="rounded-lg border border-gold-500/30 bg-gold-500/5 p-6">
          <h2 className="font-display text-2xl text-navy-900">Important disclaimer</h2>
          <p className="mt-3 text-sm leading-relaxed text-ink-700 sm:text-base">
            {ADVISORY_DISCLAIMER_LONG}
          </p>
        </div>
      </Section>

      <CtaBand
        title="Become a Mortgage Readiness Partner."
        description="Book a short briefing for production, ops, and compliance—or open the lender workspace."
        primaryHref="/contact?intent=lender"
        primaryLabel="Book a discovery call"
        secondaryHref="/lender/login"
        secondaryLabel="Lender login"
      />
    </>
  );
}
