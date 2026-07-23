import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'For Borrowers',
  description:
    'A dignified path to becoming lending ready—guided by trusted lenders, operators, and advisors using Lending Readiness Partners.',
  path: '/borrowers',
});

const personas = [
  {
    title: 'Near-miss homebuyers',
    body: 'You’re close to qualifying and need clear milestones—not conflicting forum advice or miracle claims.',
  },
  {
    title: 'Rebuild journeys',
    body: 'You’re returning after hardship and want a disciplined path back, with evidence of progress over time.',
  },
  {
    title: 'Self-employed borrowers',
    body: 'Your income is strong but your file is complex. You need credit readiness aligned with documentation readiness.',
  },
  {
    title: 'Family-focused buyers',
    body: 'You’re building housing stability for your household and need a transparent plan without predatory pressure.',
  },
];

export default function BorrowersPage() {
  return (
    <>
      <PageHero
        eyebrow="For borrowers"
        title="A clearer path to becoming lending ready."
        description="Lending Readiness Partners works through the professionals you already trust—lenders, credit operators, and realtors—so progress is measured, explained, and respectful of your goals."
        actions={
          <Button href="/contact?intent=general" variant="inverse" size="lg">
            Find a readiness partner
          </Button>
        }
      />

      <Section tone="white">
        <SectionHeading
          eyebrow="What to expect"
          title="Dignity first. Evidence always. No miracle claims."
          description="We do not promise overnight score jumps or guaranteed approvals. We help your advisors show what stands between you and lending ready—and what happens next."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'Plain-language stages',
              body: 'Understand whether you’re in diagnosis, remediation, partner review, or advancement—without jargon dumps.',
            },
            {
              title: 'Human oversight',
              body: 'Sensitive credit work is reviewed by professionals. You are never reduced to an unsupervised black box.',
            },
            {
              title: 'Shared accountability',
              body: 'Your realtor, lender, and credit partner can work from the same readiness language—so timelines stay honest.',
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
          eyebrow="Who we designed for"
          title="Borrower journeys we take seriously."
        />
        <div className="mt-10 grid gap-6 sm:grid-cols-2">
          {personas.map((persona) => (
            <article key={persona.title} className="rounded-lg bg-white p-6 ring-1 ring-navy-900/8">
              <h3 className="font-medium text-navy-900">{persona.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-700">{persona.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section tone="white">
        <SectionHeading
          title="How to get started"
          description="Ask your realtor or lender whether they work with a Lending Readiness Partners operator. If you are an advisor looking to support clients, book a partner briefing."
        />
        <div className="mt-8 flex flex-wrap gap-3">
          <Button href="/realtors" variant="secondary">
            Realtor programs
          </Button>
          <Button href="/lenders" variant="secondary">
            Lender programs
          </Button>
          <Button href="/contact" variant="primary">
            Contact partnerships
          </Button>
        </div>
      </Section>

      <CtaBand
        title="Borrowers succeed when partners share one readiness language."
        description="If you advise clients on the path to funding, we’ll help you deliver clarity without overpromising."
        primaryLabel="Book a partner briefing"
      />
    </>
  );
}
