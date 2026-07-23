'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useId, useState } from 'react';
import { Logo } from '@/components/brand/Logo';
import { Button } from '@/components/ui/Button';
import { Container } from '@/components/ui/Container';
import { primaryNav, secondaryNav } from '@/lib/site';
import { cn } from '@/lib/utils';

const desktopLinks = [
  ...primaryNav.filter((item) =>
    ['/lenders', '/partners', '/realtors', '/technology', '/pricing', '/resources'].includes(
      item.href,
    ),
  ),
  { href: '/about', label: 'About' },
];

export function Header() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const menuId = useId();

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  function closeMenu() {
    setOpen(false);
  }

  return (
    <header className="sticky top-0 z-50 border-b border-gold-500/25 bg-sand-100/95 backdrop-blur-md">
      <Container className="flex h-16 items-center justify-between gap-4 lg:h-[4.25rem]">
        <Logo />

        <nav aria-label="Primary" className="hidden items-center gap-1 lg:flex">
          {desktopLinks.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  active
                    ? 'bg-navy-900/5 text-navy-900'
                    : 'text-ink-700 hover:bg-navy-900/5 hover:text-navy-900',
                )}
                aria-current={active ? 'page' : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-2 lg:flex">
          <Button href="/portal/login" variant="ghost" size="md">
            Portal login
          </Button>
          <Button href="/contact" variant="primary" size="md">
            Book a briefing
          </Button>
        </div>

        <button
          type="button"
          className="inline-flex h-10 w-10 items-center justify-center rounded-md text-navy-900 hover:bg-navy-900/5 lg:hidden"
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((value) => !value)}
        >
          <span className="sr-only">{open ? 'Close menu' : 'Open menu'}</span>
          <span aria-hidden className="flex flex-col gap-1.5">
            <span
              className={cn(
                'block h-0.5 w-5 bg-current transition',
                open && 'translate-y-2 rotate-45',
              )}
            />
            <span className={cn('block h-0.5 w-5 bg-current transition', open && 'opacity-0')} />
            <span
              className={cn(
                'block h-0.5 w-5 bg-current transition',
                open && '-translate-y-2 -rotate-45',
              )}
            />
          </span>
        </button>
      </Container>

      <div
        id={menuId}
        className={cn(
          'border-t border-navy-900/8 bg-sand-100 lg:hidden',
          open ? 'block' : 'hidden',
        )}
      >
        <Container className="flex flex-col gap-1 py-4">
          {[...primaryNav, ...secondaryNav].map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={closeMenu}
                className={cn(
                  'rounded-md px-3 py-3 text-base font-medium',
                  active ? 'bg-navy-900/5 text-navy-900' : 'text-ink-700',
                )}
                aria-current={active ? 'page' : undefined}
              >
                {item.label}
              </Link>
            );
          })}
          <div className="mt-3 flex flex-col gap-2 border-t border-navy-900/8 pt-4">
            <Button href="/portal/login" variant="secondary" className="w-full" onClick={closeMenu}>
              Portal login
            </Button>
            <Button href="/contact" variant="primary" className="w-full" onClick={closeMenu}>
              Book a briefing
            </Button>
          </div>
        </Container>
      </div>
    </header>
  );
}
