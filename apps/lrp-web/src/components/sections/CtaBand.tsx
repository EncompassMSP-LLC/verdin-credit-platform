import { Button } from '@/components/ui/Button';
import { Section } from '@/components/ui/Section';

export function CtaBand({
  title = 'Ready to help more borrowers become lending ready?',
  description = 'Bring your production, operations, and compliance stakeholders to a 30-minute readiness briefing tailored to your channel.',
  primaryHref = '/contact',
  primaryLabel = 'Book a readiness briefing',
  secondaryHref = '/technology',
  secondaryLabel = 'See how readiness works',
}: {
  title?: string;
  description?: string;
  primaryHref?: string;
  primaryLabel?: string;
  secondaryHref?: string;
  secondaryLabel?: string;
}) {
  return (
    <Section tone="navy" className="relative overflow-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-0 right-0 w-1/2 bg-[radial-gradient(circle_at_top_right,rgba(194,158,91,0.22),transparent_55%)]"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute right-10 top-10 hidden gap-2 sm:flex"
      >
        <span className="h-3 w-3 rotate-45 bg-white/20" />
        <span className="h-3 w-3 rotate-45 bg-gold-500" />
      </div>
      <div className="relative max-w-3xl">
        <p className="eyebrow text-gold-400">Partnership briefing</p>
        <h2 className="mt-3 font-sans text-3xl font-semibold uppercase tracking-[0.05em] text-white sm:text-4xl">
          {title}
        </h2>
        <div className="mt-5 h-px w-24 bg-gold-500" aria-hidden />
        <p className="mt-5 max-w-2xl font-display text-lg italic leading-relaxed text-white/75">
          {description}
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Button href={primaryHref} variant="inverse" size="lg">
            {primaryLabel}
          </Button>
          <Button
            href={secondaryHref}
            variant="ghost"
            size="lg"
            className="text-white ring-1 ring-inset ring-white/25 hover:bg-white/10"
          >
            {secondaryLabel}
          </Button>
        </div>
      </div>
    </Section>
  );
}
