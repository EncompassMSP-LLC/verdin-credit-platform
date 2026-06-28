import type { HTMLAttributes, ReactNode } from 'react';

import { cn } from '../../lib/cn';

export interface AppShellProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/** Root layout container for application shells. */
export function AppShell({ className, children, ...props }: AppShellProps) {
  return (
    <div className={cn('flex min-h-screen bg-gray-50', className)} {...props}>
      {children}
    </div>
  );
}

export interface SidebarProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
  width?: 'sm' | 'md' | 'lg';
}

const sidebarWidths = {
  sm: 'w-56',
  md: 'w-64',
  lg: 'w-72',
} as const;

/** Sidebar column — pass navigation and branding as children. */
export function Sidebar({ className, children, width = 'md', ...props }: SidebarProps) {
  return (
    <aside
      className={cn('relative flex shrink-0 flex-col', sidebarWidths[width], className)}
      {...props}
    >
      {children}
    </aside>
  );
}

export interface MainProps extends HTMLAttributes<HTMLElement> {
  children: ReactNode;
}

/** Primary content area beside a sidebar. */
export function Main({ className, children, ...props }: MainProps) {
  return (
    <main className={cn('flex-1 overflow-auto', className)} {...props}>
      {children}
    </main>
  );
}

export interface ShellHeaderProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/** Optional top bar within the main content column. */
export function ShellHeader({ className, children, ...props }: ShellHeaderProps) {
  return (
    <header className={cn('border-b border-gray-200 bg-white px-6 py-4', className)} {...props}>
      {children}
    </header>
  );
}

export interface ShellContentProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
}

/** Padded content region inside the main column. */
export function ShellContent({ className, children, ...props }: ShellContentProps) {
  return (
    <div className={cn('p-8', className)} {...props}>
      {children}
    </div>
  );
}
