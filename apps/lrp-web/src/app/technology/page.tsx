import { ReadinessBoard } from '@/components/brand/ReadinessBoard';
import { FadeIn } from '@/components/motion/FadeIn';
import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Technology',
  description:
    'Lending readiness technology for diagnosis, mediated workflows, partner signals, and auditable exports.',
  path: '/technology',
});

export default function TechnologyPage() {
  return (
    <>
      <PageHero
        eyebrow="Technology"
        title="From credit complexity to readiness you can explain."
        description="A platform foundation for diagnosing blockers, orchestrating staff-mediated work, signaling partner-ready status, and advancing qualified borrowers with institutional controls."
        actions={
          <>
            <Button href="/contact" variant="inverse" size="lg">
              Request a walkthrough
            </Button>
            <Button
              href="/portal/login"
              variant="ghost"
              size="lg"
              className="text-white hover:bg-white/10"
            >
              Portal login
            </Button>
          </>
        }
      />

      <Section tone="white">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <SectionHeading
              eyebrow="Operating path"
              title="Four stages. One shared language."
              description="Every surface—lender, operator, advisor—maps to the same readiness path so status stops meaning five different things."
            />
            <ul className="mt-8 space-y-4">
              {[
                ['Diagnose', 'Blockers, findings, and prioritized actions'],
                ['Orchestrate', 'Roles, handoffs, and mediated execution'],
                ['Signal', 'Partner-ready status and explainable summaries'],
                ['Advance', 'Controlled progression toward funding review'],
              ].map(([title, body]) => (
                <li key={title} className="border-l-2 border-teal-600 pl-4">
                  <p className="font-medium text-navy-900">{title}</p>
                  <p className="mt-1 text-sm text-ink-700">{body}</p>
                </li>
              ))}
            </ul>
          </div>
          <FadeIn>
            <ReadinessBoard />
          </FadeIn>
        </div>
      </Section>

      <Section>
        <SectionHeading eyebrow="Platform capabilities" title="Built for institutional reality." />
        <div className="mt-10 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {[
            {
              title: 'Readiness diagnosis',
              body: 'Surface explainable gaps across credit and file signals with prioritized next actions.',
            },
            {
              title: 'Partner workflows',
              body: 'Coordinate lender, operator, and advisor roles with consistent status and ownership.',
            },
            {
              title: 'Readiness export',
              body: 'Generate summaries suitable for lender review—evidence first, hype never.',
            },
            {
              title: 'Access controls',
              body: 'Role-based permissions and least-privilege patterns for sensitive credit operations.',
            },
            {
              title: 'Auditability',
              body: 'Event history designed for operations review and vendor diligence conversations.',
            },
            {
              title: 'Mediated high-risk steps',
              body: 'Human gates where judgment and regulation require oversight—not unsupervised theater.',
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
        <SectionHeading
          eyebrow="Trust posture"
          title="Stewardship is a product requirement."
          description="Credit and lending data demand institutional care. Our approach prioritizes least-privilege access, audit trails, and human gates where judgment requires them. We do not sell borrower data or promise funding outcomes."
        />
        <div className="mt-8">
          <Button href="/contact?resource=trust-overview" variant="secondary">
            Request the trust overview
          </Button>
        </div>
      </Section>

      <CtaBand
        title="See the platform on your near-miss segment."
        description="We’ll walk production, ops, and compliance through a readiness path mapped to your channel."
      />
    </>
  );
}
