import type { ReactNode } from 'react';
import { Container } from '@/components/ui/Container';
import { cn } from '@/lib/utils';

export function PageHero({
  eyebrow,
  title,
  description,
  actions,
  tone = 'navy',
}: {
  eyebrow?: string;
  title: string;
  description: string;
  actions?: ReactNode;
  tone?: 'navy' | 'sand';
}) {
  const isNavy = tone === 'navy';

  return (
    <header
      className={cn(
        'relative overflow-hidden border-b',
        isNavy
          ? 'border-gold-500/25 bg-path-gradient text-white'
          : 'border-navy-900/8 bg-sand-100 text-navy-900',
      )}
    >
      {isNavy ? (
        <>
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_20%_0%,rgba(194,158,91,0.16),transparent_45%)]"
          />
          <div
            aria-hidden
            className="pointer-events-none absolute right-8 top-8 hidden gap-2 sm:flex"
          >
            <span className="h-3 w-3 rotate-45 bg-slate-500/50" />
            <span className="h-3 w-3 rotate-45 bg-gold-500" />
          </div>
        </>
      ) : null}
      <Container className="relative py-16 sm:py-20 lg:py-24">
        {eyebrow ? (
          <p className={cn('eyebrow', isNavy ? 'text-gold-400' : 'text-gold-600')}>{eyebrow}</p>
        ) : null}
        <h1
          className={cn(
            'mt-4 max-w-4xl font-sans text-3xl font-semibold uppercase tracking-[0.06em] sm:text-4xl lg:text-5xl lg:leading-[1.15]',
            isNavy ? 'text-white' : 'text-navy-900',
          )}
        >
          {title}
        </h1>
        <div className="mt-5 h-px w-24 bg-gold-500" aria-hidden />
        <p
          className={cn(
            'mt-5 max-w-2xl font-display text-lg italic leading-relaxed sm:text-xl',
            isNavy ? 'text-white/80' : 'text-ink-700',
          )}
        >
          {description}
        </p>
        {actions ? <div className="mt-8 flex flex-wrap gap-3">{actions}</div> : null}
      </Container>
    </header>
  );
}
