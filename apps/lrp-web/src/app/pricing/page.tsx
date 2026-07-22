import { CtaBand } from '@/components/sections/CtaBand';
import { PageHero } from '@/components/sections/PageHero';
import { Button } from '@/components/ui/Button';
import { Section, SectionHeading } from '@/components/ui/Section';
import { pricingTiers } from '@/content/pricing';
import { createMetadata } from '@/lib/seo';
import { cn } from '@/lib/utils';

export const metadata = createMetadata({
  title: 'Pricing',
  description:
    'Operator, Lender, and Network packages for Lending Readiness Partners—transparent platform pricing with enterprise options.',
  path: '/pricing',
});

export default function PricingPage() {
  return (
    <>
      <PageHero
        eyebrow="Pricing"
        title="Packages built for operators, lenders, and networks."
        description="Annual platform agreements with implementation support. Enterprise and multi-region deployments are scoped through a readiness briefing."
      />

      <Section tone="white">
        <div className="grid gap-6 lg:grid-cols-3">
          {pricingTiers.map((tier) => (
            <article
              key={tier.id}
              className={cn(
                'flex h-full flex-col rounded-lg p-6 ring-1 sm:p-8',
                tier.highlighted
                  ? 'bg-navy-900 text-white ring-navy-900'
                  : 'bg-sand-50 text-ink-900 ring-navy-900/10',
              )}
            >
              <p
                className={cn(
                  'text-xs font-medium uppercase tracking-eyebrow',
                  tier.highlighted ? 'text-gold-400' : 'text-gold-600',
                )}
              >
                {tier.name}
              </p>
              <div className="mt-4 flex items-baseline gap-2">
                <span className="font-display text-4xl font-medium">{tier.price}</span>
              </div>
              <p
                className={cn(
                  'mt-1 text-sm',
                  tier.highlighted ? 'text-white/65' : 'text-slate-500',
                )}
              >
                {tier.cadence}
              </p>
              <p
                className={cn(
                  'mt-4 text-sm leading-relaxed',
                  tier.highlighted ? 'text-white/80' : 'text-ink-700',
                )}
              >
                {tier.description}
              </p>
              <ul className="mt-6 flex-1 space-y-3">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex gap-2 text-sm">
                    <span
                      className={cn(
                        'mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full',
                        tier.highlighted ? 'bg-gold-400' : 'bg-gold-500',
                      )}
                      aria-hidden
                    />
                    <span className={tier.highlighted ? 'text-white/85' : 'text-ink-700'}>
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Button
                  href={tier.cta.href}
                  variant={tier.highlighted ? 'inverse' : 'primary'}
                  className="w-full"
                >
                  {tier.cta.label}
                </Button>
              </div>
            </article>
          ))}
        </div>
        <p className="mt-8 text-sm text-slate-500">
          Prices shown are starting platform fees for standard deployments in the United States and
          exclude optional professional services beyond the included implementation playbook. Final
          commercials depend on volume, regions, and security requirements.
        </p>
      </Section>

      <Section>
        <SectionHeading
          title="What every package includes"
          description="Claim guardrails, mediated-control design, partner stage language, and access to readiness briefing support during onboarding."
        />
        <div className="mt-8 flex flex-wrap gap-3">
          <Button href="/contact" variant="primary">
            Talk through fit
          </Button>
          <Button href="/faqs" variant="secondary">
            Read FAQs
          </Button>
        </div>
      </Section>

      <CtaBand
        title="Not sure which package fits?"
        description="Bring your volume and channel model to a briefing—we’ll recommend Operator, Lender, or Network without the hard sell."
      />
    </>
  );
}
