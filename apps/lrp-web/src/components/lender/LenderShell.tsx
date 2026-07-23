'use client';

import Image from 'next/image';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LogOut, Menu, X } from 'lucide-react';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { LenderNavIcon } from '@/components/lender/LenderNavIcon';
import { AdvisoryDisclaimer } from '@/components/ui/AdvisoryDisclaimer';
import { useLenderAuth } from '@/lib/lender/auth';
import { notifications } from '@/lib/lender/data';
import { lenderNav } from '@/lib/lender/nav';
import { cn } from '@/lib/utils';

const groupLabels = {
  operations: 'Operations',
  insights: 'Insights',
  governance: 'Governance',
} as const;

export function LenderShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isLoading, isAuthenticated, logout, can, authMode } = useLenderAuth();
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace(`/lender/login?redirect=${encodeURIComponent(pathname)}`);
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  const visibleNav = useMemo(() => lenderNav.filter((item) => can(item.permission)), [can]);

  const unread = notifications.filter((n) => !n.read).length;

  function signOut() {
    logout();
    router.push('/lender/login');
    router.refresh();
  }

  if (isLoading || !isAuthenticated || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-lrp-surface text-sm text-slate-500">
        Loading lender workspace…
      </div>
    );
  }

  const groups = (['operations', 'insights', 'governance'] as const).map((group) => ({
    group,
    items: visibleNav.filter((item) => item.group === group),
  }));

  return (
    <div className="lrp-shell-surface">
      <a
        href="#lender-main"
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
              href="/lender/dashboard"
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
                  Lender
                </span>
                <span className="block text-sm font-semibold tracking-tight">Workspace</span>
              </span>
            </Link>
            <button
              type="button"
              className="rounded-md p-2 lg:hidden"
              onClick={() => setOpen(false)}
              aria-label="Close navigation"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav aria-label="Lender workspace" className="flex-1 overflow-y-auto px-3 py-4">
            {groups.map(({ group, items }) =>
              items.length ? (
                <div key={group} className="mb-5">
                  <p className="px-3 pb-2 text-[0.65rem] font-semibold uppercase tracking-[0.14em] text-white/40">
                    {groupLabels[group]}
                  </p>
                  <ul className="space-y-0.5">
                    {items.map((item) => {
                      const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
                      return (
                        <li key={item.href}>
                          <Link
                            href={item.href}
                            onClick={() => setOpen(false)}
                            className={cn(
                              'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition',
                              active
                                ? 'bg-gold-500 text-navy-900'
                                : 'text-white/75 hover:bg-white/10 hover:text-white',
                            )}
                            aria-current={active ? 'page' : undefined}
                          >
                            <LenderNavIcon name={item.icon} className="h-4 w-4 shrink-0" />
                            <span className="flex-1">{item.label}</span>
                          </Link>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              ) : null,
            )}
          </nav>

          <div className="border-t border-white/10 p-4">
            <p className="truncate text-sm font-medium">{user.displayName}</p>
            <p className="truncate text-xs text-white/55">{user.organizationName}</p>
            <p className="mt-0.5 truncate text-xs text-gold-400/90">{user.title}</p>
            <button
              type="button"
              onClick={signOut}
              className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-gold-400 hover:underline"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>
        </aside>

        {open ? (
          <button
            type="button"
            className="fixed inset-0 z-30 bg-navy-900/50 lg:hidden"
            aria-label="Close menu overlay"
            onClick={() => setOpen(false)}
          />
        ) : null}

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-20 flex h-16 items-center justify-between gap-3 border-b border-lrp-border bg-lrp-surface/95 px-4 backdrop-blur sm:px-6">
            <div className="flex min-w-0 items-center gap-3">
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-md border border-lrp-border bg-lrp-surface-elevated lg:hidden"
                onClick={() => setOpen(true)}
                aria-label="Open navigation"
              >
                <Menu className="h-5 w-5" />
              </button>
              <div className="min-w-0">
                <p className="truncate text-[0.65rem] font-medium uppercase tracking-eyebrow text-gold-600">
                  {user.organizationName} · Partner edition
                  {authMode === 'demo'
                    ? ' · demo auth'
                    : authMode === 'platform'
                      ? ' · platform'
                      : ''}
                </p>
                <p className="truncate text-sm font-semibold">
                  Helping More Borrowers Become Lending Ready.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Link
                href="/lender/notifications"
                className="relative inline-flex h-9 w-9 items-center justify-center rounded-md border border-lrp-border bg-lrp-surface-elevated"
                aria-label="Notifications"
              >
                <LenderNavIcon name="notifications" className="h-4 w-4" />
                {unread > 0 ? (
                  <span className="absolute -right-1 -top-1 inline-flex h-4 min-w-4 items-center justify-center rounded-full bg-critical px-1 text-[0.6rem] font-bold text-white">
                    {unread}
                  </span>
                ) : null}
              </Link>
            </div>
          </header>

          <AdvisoryDisclaimer href="/technology" />

          <main id="lender-main" className="flex-1 px-4 py-6 sm:px-6 lg:px-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
