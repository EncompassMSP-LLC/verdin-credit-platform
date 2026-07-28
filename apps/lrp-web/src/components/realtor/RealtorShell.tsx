'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LogOut, Menu, X } from 'lucide-react';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { AdvisoryDisclaimer } from '@/components/ui/AdvisoryDisclaimer';
import { useRealtorAuth } from '@/lib/realtor/auth';
import { realtorNav } from '@/lib/realtor/nav';
import { cn } from '@/lib/utils';

export function RealtorShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, isAuthenticated, logout, can } = useRealtorAuth();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(`/realtor/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  const visibleNav = useMemo(() => realtorNav.filter((item) => can(item.permission)), [can]);

  function signOut() {
    logout();
    router.push('/realtor/login');
    router.refresh();
  }

  if (isLoading || !isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-lrp-surface text-sm text-slate-500">
        Loading realtor workspace…
      </div>
    );
  }

  return (
    <div className="lrp-shell-surface">
      <a
        href="#realtor-main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[60] focus:rounded-md focus:bg-white focus:px-3 focus:py-2 focus:text-sm"
      >
        Skip to content
      </a>

      <div className="flex min-h-screen">
        <aside
          className={cn(
            'fixed inset-y-0 left-0 z-40 flex w-[17.5rem] flex-col border-r border-navy-900/10 bg-navy-900 text-white transition-transform lg:static lg:translate-x-0',
            open ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className="flex items-center justify-between gap-3 border-b border-white/10 px-5 py-4">
            <Link
              href="/realtor/dashboard"
              className="flex items-center gap-3"
              onClick={() => setOpen(false)}
            >
              <Image
                src="/brand/logo-icon.png"
                alt=""
                width={36}
                height={36}
                className="h-9 w-9 rounded-md bg-white/10 object-contain p-0.5"
              />
              <span className="leading-tight">
                <span className="block text-[0.65rem] font-semibold uppercase tracking-[0.16em] text-gold-400">
                  Realtor
                </span>
                <span className="block text-sm font-semibold tracking-tight">Workspace</span>
              </span>
            </Link>
            <button
              type="button"
              className="rounded-md p-2 lg:hidden"
              onClick={() => setOpen(false)}
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
            {visibleNav.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setOpen(false)}
                  className={cn(
                    'block rounded-md px-3 py-2 text-sm font-medium transition',
                    active
                      ? 'bg-white/15 text-white'
                      : 'text-white/70 hover:bg-white/10 hover:text-white',
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="border-t border-white/10 px-4 py-4">
            <p className="truncate text-sm font-medium">{user.displayName}</p>
            <p className="truncate text-xs text-white/55">{user.organizationName}</p>
            <button
              type="button"
              onClick={signOut}
              className="mt-3 inline-flex items-center gap-2 text-xs font-medium text-gold-400 hover:text-gold-300"
            >
              <LogOut className="h-3.5 w-3.5" />
              Sign out
            </button>
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center gap-3 border-b border-lrp-border bg-lrp-surface-elevated px-4 py-3 lg:px-6">
            <button
              type="button"
              className="rounded-md border border-lrp-border p-2 lg:hidden"
              onClick={() => setOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-navy-900">
                {user.partnershipDisplayName}
              </p>
              <p className="truncate text-xs text-slate-500">Coarse referral status only</p>
            </div>
          </header>
          <main id="realtor-main" className="flex-1 px-4 py-6 lg:px-8">
            {children}
            <div className="mt-10">
              <AdvisoryDisclaimer />
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
