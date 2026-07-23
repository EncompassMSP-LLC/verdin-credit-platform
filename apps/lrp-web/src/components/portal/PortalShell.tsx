'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Menu, LogOut, X } from 'lucide-react';
import { useEffect, useState, type ReactNode } from 'react';
import { PortalNavIcon } from '@/components/portal/PortalNavIcon';
import { AdvisoryDisclaimer } from '@/components/ui/AdvisoryDisclaimer';
import { usePlatformAuth } from '@/lib/platform/auth';
import { portalNav } from '@/lib/portal/nav';
import { cn } from '@/lib/utils';

export function PortalShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, isAuthenticated, logout } = usePlatformAuth();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(`/portal/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  function signOut() {
    logout();
    router.push('/portal/login');
    router.refresh();
  }

  if (isLoading || !isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-lrp-surface text-sm text-slate-500">
        Connecting to platform…
      </div>
    );
  }

  const displayName = user.client_display_name || user.email;

  return (
    <div className="lrp-shell-surface">
      <a
        href="#portal-main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-brand focus:bg-white focus:px-3 focus:py-2 focus:text-sm focus:text-navy-900"
      >
        Skip to portal content
      </a>

      <div className="flex min-h-screen">
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-40 flex w-72 flex-col border-r border-lrp-border bg-lrp-surface-elevated transition-transform lg:static lg:translate-x-0',
            open ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className="flex items-center justify-between gap-3 border-b border-lrp-border px-5 py-4">
            <Link
              href="/portal/dashboard"
              className="flex items-center gap-3"
              onClick={() => setOpen(false)}
            >
              <Image
                src="/brand/logo-icon.png"
                alt=""
                width={36}
                height={36}
                className="h-9 w-9 rounded-brand bg-lrp-surface object-contain"
              />
              <span className="leading-tight">
                <span className="block text-[0.65rem] font-semibold uppercase tracking-[0.16em]">
                  Borrower
                </span>
                <span className="block text-[0.7rem] font-medium uppercase tracking-[0.2em] text-gold-600">
                  Portal
                </span>
              </span>
            </Link>
            <button
              type="button"
              className="rounded-brand p-2 lg:hidden"
              onClick={() => setOpen(false)}
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav aria-label="Borrower portal" className="flex-1 overflow-y-auto px-3 py-4">
            <ul className="space-y-1">
              {portalNav.map((item) => {
                const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={() => setOpen(false)}
                      className={cn(
                        'flex items-center gap-3 rounded-brand px-3 py-2.5 text-sm font-medium transition duration-brand',
                        active ? 'bg-navy-900 text-white' : 'text-ink-700 hover:bg-lrp-surface',
                      )}
                      aria-current={active ? 'page' : undefined}
                    >
                      <PortalNavIcon name={item.icon} className="h-4 w-4 shrink-0" />
                      <span className="flex-1">{item.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="border-t border-lrp-border p-4">
            <p className="truncate text-sm font-medium">{displayName}</p>
            <p className="truncate text-xs text-slate-500">{user.email}</p>
            <button
              type="button"
              onClick={signOut}
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-gold-700 hover:underline"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>

        {open ? (
          <button
            type="button"
            className="fixed inset-0 z-30 bg-navy-900/40 lg:hidden"
            aria-label="Close menu overlay"
            onClick={() => setOpen(false)}
          />
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b border-lrp-border bg-lrp-surface/90 px-4 backdrop-blur sm:px-6">
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-brand border border-lrp-border bg-lrp-surface-elevated lg:hidden"
                onClick={() => setOpen(true)}
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div>
                <p className="text-[0.65rem] font-medium uppercase tracking-eyebrow text-gold-600">
                  Shared platform session
                </p>
                <p className="text-sm font-semibold text-navy-900">
                  Helping More Borrowers Become Lending Ready.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/portal/notifications"
                className="relative inline-flex h-9 w-9 items-center justify-center rounded-brand border border-lrp-border bg-lrp-surface-elevated"
                aria-label="Notifications"
              >
                <PortalNavIcon name="notifications" className="h-4 w-4" />
              </Link>
            </div>
          </header>

          <AdvisoryDisclaimer href="/portal/readiness" />

          <main id="portal-main" className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
