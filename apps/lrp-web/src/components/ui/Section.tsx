import type { ReactNode } from 'react';
import { Container } from '@/components/ui/Container';
import { cn } from '@/lib/utils';

export function Section({
  children,
  className,
  id,
  tone = 'sand',
}: {
  children: ReactNode;
  className?: string;
  id?: string;
  tone?: 'sand' | 'white' | 'navy';
}) {
  const tones = {
    sand: 'bg-sand-100 text-ink-900',
    white: 'bg-white text-ink-900',
    navy: 'bg-navy-900 text-white',
  };

  return (
    <section id={id} className={cn('py-16 sm:py-20 lg:py-24', tones[tone], className)}>
      <Container>{children}</Container>
    </section>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
  invert = false,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  align?: 'left' | 'center';
  invert?: boolean;
}) {
  return (
    <div className={cn(align === 'center' && 'mx-auto max-w-3xl text-center')}>
      {eyebrow ? <p className={cn('eyebrow', invert && 'text-teal-400')}>{eyebrow}</p> : null}
      <h2
        className={cn(
          'mt-3 font-sans text-2xl font-semibold uppercase tracking-[0.05em] sm:text-3xl lg:text-4xl',
          invert ? 'text-white' : 'text-navy-900',
        )}
      >
        {title}
      </h2>
      <div
        className={cn(
          'mt-4 h-px w-16',
          invert ? 'bg-gold-400' : 'bg-gold-500',
          align === 'center' && 'mx-auto',
        )}
        aria-hidden
      />
      {description ? (
        <p
          className={cn(
            'mt-4 font-display text-base italic leading-relaxed sm:text-lg',
            invert ? 'text-white/75' : 'text-ink-700',
            align === 'center' && 'mx-auto max-w-2xl',
          )}
        >
          {description}
        </p>
      ) : null}
    </div>
  );
}
