import Image from 'next/image';
import Link from 'next/link';
import { siteConfig } from '@/lib/site';
import { cn } from '@/lib/utils';

export function Logo({
  variant = 'dark',
  className,
  showTagline = false,
}: {
  variant?: 'dark' | 'light';
  className?: string;
  showTagline?: boolean;
}) {
  const isLight = variant === 'light';

  return (
    <Link
      href="/"
      className={cn('inline-flex items-center gap-3 focus-visible:rounded-sm', className)}
      aria-label={`${siteConfig.name} home`}
    >
      <span
        className={cn(
          'relative flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-brand',
          isLight ? 'bg-white/95 ring-1 ring-gold-500/40' : 'bg-sand-100',
        )}
      >
        <Image
          src="/brand/logo-icon.png"
          alt=""
          width={44}
          height={44}
          className="h-10 w-10 object-contain"
          priority
        />
      </span>
      <span className="flex flex-col leading-none">
        <span
          className={cn(
            'font-sans text-[0.72rem] font-semibold uppercase tracking-[0.14em] sm:text-[0.8rem]',
            isLight ? 'text-white' : 'text-navy-900',
          )}
        >
          Lending Readiness
        </span>
        <span className="mt-1.5 flex items-center gap-2">
          <span className="h-px w-4 bg-gold-500" aria-hidden />
          <span className="font-sans text-[0.62rem] font-medium uppercase tracking-[0.28em] text-gold-500 sm:text-[0.68rem]">
            Partners
          </span>
          <span className="h-px w-4 bg-gold-500" aria-hidden />
        </span>
        {showTagline ? (
          <span
            className={cn(
              'mt-2 max-w-[16rem] text-[0.68rem] leading-snug',
              isLight ? 'text-white/65' : 'text-slate-500',
            )}
          >
            Premium Financial Technology
          </span>
        ) : null}
      </span>
    </Link>
  );
}
