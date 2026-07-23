import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  title: 'Services',
  description:
    'Lending readiness services spanning diagnosis, mediated workflows, partner enablement, and enterprise implementation.',
  path: '/services',
});

const services = [
  {
    title: 'Readiness diagnosis',
    body: 'Identify credit and file blockers, prioritize actions, and establish a shared definition of lending ready for each segment.',
  },
  {
    title: 'Mediated workflow operations',
    body: 'Coordinate staff-reviewed credit work with ownership, timelines, and audit history suitable for institutional partners.',
  },
  {
    title: 'Lender workspace enablement',
    body: 'Stand up near-miss pipeline views, readiness exports, and stakeholder training for production, ops, and credit risk.',
  },
  {
    title: 'Operator workbench packaging',
    body: 'Productize mortgage readiness for channel partners with status standards and partner-kit collateral.',
  },
  {
    title: 'Realtor partner programs',
    body: 'Deploy expectation-setting scripts, stage glossaries, and preferred-partner operating cadences.',
  },
  {
    title: 'Pilot & change management',
    body: 'Run 60-day controlled pilots with success metrics, governance checkpoints, and rollout playbooks.',
  },
];

export default function ServicesPage() {
  return (
    <>
      <PageHero
        eyebrow="Services"
        title="Services that turn readiness into an operating rhythm."
        description="From diagnosis to partner enablement, our services help lenders and operators convert near-miss volume into evidenced progress—without compromising compliance posture."
        actions={
          <Button href="/contact" variant="inverse" size="lg">
            Scope a service engagement
          </Button>
        }
      />

      <Section tone="white">
        <div className="grid gap-6 md:grid-cols-2">
          {services.map((service) => (
            <article
              key={service.title}
              className="rounded-lg border border-navy-900/8 bg-sand-50 p-6"
            >
              <h2 className="font-display text-2xl text-navy-900">{service.title}</h2>
              <p className="mt-3 text-sm leading-relaxed text-ink-700 sm:text-base">
                {service.body}
              </p>
            </article>
          ))}
        </div>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Engagement model"
          title="Briefing → pilot → rollout."
          description="We start with a readiness briefing, define a near-miss segment and success metrics, then expand only after controls and outcomes prove out."
        />
        <div className="mt-8 flex flex-wrap gap-3">
          <Button href="/technology" variant="secondary">
            Review technology
          </Button>
          <Button href="/pricing" variant="secondary">
            Compare packages
          </Button>
          <Button href="/contact" variant="primary">
            Book a briefing
          </Button>
        </div>
      </Section>

      <CtaBand />
    </>
  );
}
