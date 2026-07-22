import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function absoluteUrl(path = '/'): string {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://lendingreadinesspartners.com';
  if (path.startsWith('http')) return path;
  return `${base.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`;
}

export function formatDate(value: string | Date, opts?: Intl.DateTimeFormatOptions) {
  const date = typeof value === 'string' ? new Date(value) : value;
  return date.toLocaleDateString(
    'en-US',
    opts ?? { month: 'short', day: 'numeric', year: 'numeric' },
  );
}

export function formatPercent(value: number) {
  return `${Math.round(value)}%`;
}
