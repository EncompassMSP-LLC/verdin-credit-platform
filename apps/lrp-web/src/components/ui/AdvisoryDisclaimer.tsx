import Link from 'next/link';
import { ADVISORY_DISCLAIMER_LONG, ADVISORY_DISCLAIMER_SHORT } from '@/lib/design-tokens';
import { cn } from '@/lib/utils';

type Props = {
  variant?: 'banner' | 'inline' | 'footer';
  href?: string;
  className?: string;
};

/**
 * Vol 18 / CLAIM-LIBRARY — required advisory language on product shells.
 */
export function AdvisoryDisclaimer({
  variant = 'banner',
  href = '/portal/readiness',
  className,
}: Props) {
  if (variant === 'inline') {
    return (
      <p className={cn('text-xs leading-relaxed text-slate-500', className)}>
        {ADVISORY_DISCLAIMER_SHORT}{' '}
        <Link href={href} className="font-medium text-gold-700 underline-offset-2 hover:underline">
          What this means
        </Link>
      </p>
    );
  }

  if (variant === 'footer') {
    return (
      <p className={cn('text-[0.7rem] leading-relaxed text-white/55', className)}>
        {ADVISORY_DISCLAIMER_SHORT}
      </p>
    );
  }

  return (
    <div
      role="note"
      className={cn(
        'border-b border-lrp-border bg-lrp-info/5 px-4 py-2 text-xs leading-relaxed text-navy-900 sm:px-6',
        className,
      )}
    >
      <span className="font-medium text-lrp-info">Advisory. </span>
      {ADVISORY_DISCLAIMER_SHORT}{' '}
      <Link
        href={href}
        className="font-medium text-gold-700 underline-offset-2 hover:underline"
        title={ADVISORY_DISCLAIMER_LONG}
      >
        Learn more
      </Link>
    </div>
  );
}
