import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'About',
  description:
    'Mission, vision, and values behind Lending Readiness Partners—helping more borrowers become lending ready.',
  path: '/about',
});

const values = [
  {
    title: 'Readiness Over Rhetoric',
    body: 'We measure progress in funded outcomes, not slogans. Clarity beats complexity. Evidence beats assumption.',
  },
  {
    title: 'Stewardship of Trust',
    body: 'Credit and lending decisions shape lives. We treat borrower data, lender judgment, and regulatory obligations with institutional care.',
  },
  {
    title: 'Shared Advantage',
    body: 'Borrowers, lenders, credit professionals, and realtors succeed together—or not at all.',
  },
  {
    title: 'Operational Excellence',
    body: 'Fortune-level brands earn authority through reliability. Our systems and service must feel precise under pressure.',
  },
  {
    title: 'Fair Access with Integrity',
    body: 'Expanding access must never mean lowering standards. We improve readiness—not obscure risk.',
  },
  {
    title: 'Partnership as Practice',
    body: 'Partners is not decorative. We co-own pipeline quality, compliance posture, and borrower experience.',
  },
];

export default function AboutPage() {
  return (
    <>
      <PageHero
        eyebrow="About Lending Readiness Partners"
        title="Partners in the path to funding."
        description="We exist to help more borrowers become lending ready—by giving lenders, operators, and advisors a clear, compliant path from credit complexity to funding confidence."
        actions={
          <>
            <Button href="/contact" variant="inverse" size="lg">
              Book a briefing
            </Button>
            <Button
              href="/technology"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Explore technology
            </Button>
          </>
        }
      />

      <Section tone="white">
        <div className="grid gap-10 lg:grid-cols-2">
          <div>
            <p className="eyebrow">Mission</p>
            <h2 className="mt-3 font-display text-3xl text-navy-900 sm:text-4xl">
              Make readiness operational.
            </h2>
            <p className="mt-4 text-ink-700">
              We convert fragmented credit data, dispute workflows, and underwriting uncertainty
              into shared readiness signals that accelerate responsible lending outcomes.
            </p>
          </div>
          <div>
            <p className="eyebrow">Vision</p>
            <h2 className="mt-3 font-display text-3xl text-navy-900 sm:text-4xl">
              A fairer, more legible path to funding.
            </h2>
            <p className="mt-4 text-ink-700">
              A lending ecosystem where readiness is visible, measurable, and fair—so qualified
              borrowers are never left behind because the system couldn’t see them clearly.
            </p>
          </div>
        </div>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Brand story"
          title="Readiness was invisible. We built the operating foundation."
          description="Every year, millions of borrowers are close to qualifying—yet fall out of the pipeline. Not always because they lack income. Often because readiness is fragmented across reports, disputes, and partner handoffs."
        />
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          {[
            {
              title: 'The insight',
              body: 'Lending readiness is a system outcome, not a single score. It lives where credit integrity, documentation, compliance, and coordination meet.',
            },
            {
              title: 'What we built',
              body: 'A shared foundation to diagnose gaps, orchestrate mediated workflows, surface readiness signals, and keep humans in the loop where judgment demands it.',
            },
            {
              title: 'What we stand for',
              body: 'More borrowers who deserve a chance become lending ready. More lenders fund with confidence. More advisors close with fewer surprises.',
            },
          ].map((item) => (
            <article key={item.title} className="rounded-lg bg-white p-6 ring-1 ring-navy-900/8">
              <h3 className="font-display text-xl text-navy-900">{item.title}</h3>
              <p className="mt-3 text-sm leading-relaxed text-ink-700">{item.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <Section tone="white">
        <SectionHeading eyebrow="Core values" title="How we decide when it matters." />
        <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {values.map((value) => (
            <article key={value.title} className="border-t-2 border-teal-600 pt-5">
              <h3 className="font-medium text-navy-900">{value.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-ink-700">{value.body}</p>
            </article>
          ))}
        </div>
      </Section>

      <CtaBand
        title="Build with a partner who treats readiness seriously."
        description="Whether you lead production, operations, or compliance, we’ll meet you with clarity—not hype."
      />
    </>
  );
}
