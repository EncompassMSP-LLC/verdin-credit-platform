import Image from 'next/image';
import { FadeIn } from '@/components/motion/FadeIn';
import { CtaBand } from '@/components/sections/CtaBand';
import { Button } from '@/components/ui/Button';
import { Container } from '@/components/ui/Container';
import { Section, SectionHeading } from '@/components/ui/Section';
import { siteConfig } from '@/lib/site';
import { createMetadata } from '@/lib/seo';

export const metadata = createMetadata({
  description: siteConfig.description,
  path: '/',
});

const pillars = [
  {
    title: 'Intelligence',
    body: 'See exactly what stands between a borrower and ready—with shared definitions across lender, operator, and realtor views.',
  },
  {
    title: 'Innovation',
    body: 'Turn fragmented credit work into auditable readiness workflows that respect institutional controls.',
  },
  {
    title: 'Integrity',
    body: 'Staff-mediated actions, claim guardrails, and evidenced progress—never approval theater.',
  },
  {
    title: 'Impact',
    body: 'Move more borrowers from almost ready to lending ready while partners protect closings and pull-through.',
  },
];

const steps = [
  {
    title: 'Diagnose',
    body: 'Identify readiness gaps across credit findings and file signals before timelines slip.',
  },
  {
    title: 'Orchestrate',
    body: 'Coordinate staff-mediated work with clear ownership, status, and accountability.',
  },
  {
    title: 'Signal',
    body: 'Share partner-ready readiness language that production and credit teams can explain.',
  },
  {
    title: 'Advance',
    body: 'Hand off qualified borrowers with fewer surprises—and judgment still where it belongs.',
  },
];

export default function HomePage() {
  return (
    <>
      <header className="relative overflow-hidden bg-path-gradient text-white">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_15%_10%,rgba(194,158,91,0.18),transparent_42%),radial-gradient(ellipse_at_90%_80%,rgba(0,120,96,0.12),transparent_40%)]"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute right-10 top-10 hidden gap-2 lg:flex"
        >
          <span className="h-3 w-3 rotate-45 bg-white/25" />
          <span className="h-3 w-3 rotate-45 bg-gold-500" />
        </div>
        <Container className="relative grid items-center gap-12 py-16 lg:grid-cols-[1.05fr_0.95fr] lg:gap-16 lg:py-24">
          <div>
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-400">
              Premium Financial Technology
            </p>
            <h1 className="mt-5 font-sans text-4xl font-semibold uppercase leading-[1.12] tracking-[0.06em] sm:text-5xl lg:text-[3.1rem]">
              Lending Readiness
              <span className="mt-3 block text-2xl font-medium tracking-[0.28em] text-gold-400 sm:text-3xl">
                Partners
              </span>
            </h1>
            <div className="mt-6 h-px w-28 bg-gold-500" aria-hidden />
            <p className="mt-6 max-w-xl font-display text-xl italic leading-relaxed text-white/85">
              Helping More Borrowers Become Lending Ready.
            </p>
            <p className="mt-4 max-w-xl text-sm leading-relaxed text-white/70 sm:text-base">
              We bridge readiness and opportunity through insight, technology, and trust— so
              lenders, operators, and advisors can move qualified borrowers forward with confidence.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button href="/contact" variant="inverse" size="lg">
                Book a readiness briefing
              </Button>
              <Button
                href="/technology"
                variant="ghost"
                size="lg"
                className="text-white ring-1 ring-inset ring-white/25 hover:bg-white/10"
              >
                See how readiness works
              </Button>
            </div>
            <p className="mt-10 text-[0.65rem] font-medium uppercase tracking-eyebrow text-white/55">
              Mortgage lenders · Banks · Credit unions · Realtors · Financial professionals
            </p>
          </div>
          <FadeIn delay={0.1} className="justify-self-center lg:justify-self-end">
            <div className="relative rounded-brand bg-sand-100/95 p-6 shadow-soft ring-1 ring-gold-500/30 sm:p-8">
              <Image
                src="/brand/logo-stacked.png"
                alt="Lending Readiness Partners logo"
                width={420}
                height={550}
                className="mx-auto h-auto w-full max-w-[280px] sm:max-w-[320px]"
                priority
              />
            </div>
          </FadeIn>
        </Container>
        <div className="relative border-t border-gold-500/25 bg-navy-900/40">
          <Container className="flex flex-wrap items-center justify-between gap-3 py-4 text-[0.65rem] font-medium uppercase tracking-eyebrow text-gold-400">
            <span>Preparing today</span>
            <span className="hidden text-white/30 sm:inline">·</span>
            <span>Positioning tomorrow</span>
            <span className="hidden text-white/30 sm:inline">·</span>
            <span>Powering possibilities</span>
          </Container>
        </div>
      </header>

      <Section tone="white">
        <div className="grid gap-10 lg:grid-cols-2 lg:gap-16">
          <FadeIn>
            <SectionHeading
              eyebrow="The problem"
              title="“Almost ready” is where good loans go to stall."
              description="Credit files are complex. Disputes take time. Underwriting needs evidence. Realtors need timelines. When those signals don’t connect, borrowers fall out—and everyone loses volume, trust, and momentum."
            />
          </FadeIn>
          <FadeIn delay={0.08}>
            <SectionHeading
              eyebrow="The foundation"
              title="Readiness is the strategy. Partnership is the advantage."
              description="Lending Readiness Partners helps your ecosystem diagnose blockers, coordinate credit operations, and share readiness clearly—without replacing lender judgment or promising outcomes you can’t defend."
            />
          </FadeIn>
        </div>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Brand pillars"
          title="Intelligence. Innovation. Integrity. Impact."
          description="Four commitments that shape every product decision, sales conversation, and partner workflow."
        />
        <div className="mt-12 grid gap-6 sm:grid-cols-2">
          {pillars.map((pillar, index) => (
            <FadeIn key={pillar.title} delay={index * 0.05}>
              <article className="h-full border-l-2 border-gold-500 bg-white p-6 shadow-soft ring-1 ring-navy-900/5">
                <h3 className="font-sans text-lg font-semibold uppercase tracking-wider text-navy-900">
                  {pillar.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-ink-700 sm:text-base">
                  {pillar.body}
                </p>
              </article>
            </FadeIn>
          ))}
        </div>
      </Section>

      <Section tone="white" id="how-it-works">
        <SectionHeading
          eyebrow="How it works"
          title="From credit complexity to readiness you can explain."
          description="A disciplined path—measured, mediated, and built for institutional trust."
        />
        <ol className="mt-12 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {steps.map((step, index) => (
            <FadeIn key={step.title} delay={index * 0.05}>
              <li className="h-full rounded-brand bg-sand-100 p-6 ring-1 ring-navy-900/8">
                <p className="font-mono text-xs font-medium text-gold-600">0{index + 1}</p>
                <h3 className="mt-3 font-sans text-xl font-semibold uppercase tracking-wide text-navy-900">
                  {step.title}
                </h3>
                <p className="mt-3 text-sm leading-relaxed text-ink-700">{step.body}</p>
              </li>
            </FadeIn>
          ))}
        </ol>
      </Section>

      <Section>
        <SectionHeading
          eyebrow="Who we serve"
          title="Built for the partners who move borrowers forward."
        />
        <div className="mt-12 grid gap-6 lg:grid-cols-3">
          {[
            {
              href: '/lenders',
              title: 'For lenders',
              body: 'Fund more near-miss borrowers with evidenced readiness—and protect underwriting integrity.',
            },
            {
              href: '/partners',
              title: 'For operators',
              body: 'Run credit operations that map to lending outcomes and partner-ready status.',
            },
            {
              href: '/realtors',
              title: 'For realtors',
              body: 'Know who’s timeline-viable. Set honest expectations. Protect closings and client trust.',
            },
          ].map((item, index) => (
            <FadeIn key={item.href} delay={index * 0.05}>
              <a
                href={item.href}
                className="group flex h-full flex-col rounded-brand bg-white p-6 shadow-soft ring-1 ring-navy-900/8 transition hover:ring-gold-500/50"
              >
                <h3 className="font-sans text-xl font-semibold uppercase tracking-wide text-navy-900 group-hover:text-gold-600">
                  {item.title}
                </h3>
                <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-700 sm:text-base">
                  {item.body}
                </p>
                <span className="mt-6 text-sm font-medium uppercase tracking-wider text-gold-600">
                  Learn more →
                </span>
              </a>
            </FadeIn>
          ))}
        </div>
      </Section>

      <CtaBand />
    </>
  );
}
