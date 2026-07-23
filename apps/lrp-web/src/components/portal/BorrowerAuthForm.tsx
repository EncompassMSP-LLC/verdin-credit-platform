'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState, type FormEvent } from 'react';
import { ApiClientError } from '@verdin/api-client';
import { usePlatformAuth } from '@/lib/platform/auth';
import { getApiBaseUrl } from '@/lib/platform/config';
import { cn } from '@/lib/utils';

const inputClass =
  'w-full rounded-brand border border-navy-900/15 bg-white px-3.5 py-2.5 text-sm text-navy-900 shadow-sm focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30 dark:border-white/15 dark:bg-navy-900 dark:text-white';

export function BorrowerAuthForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/portal/dashboard';
  const { login } = usePlatformAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email.trim(), password);
      router.push(redirectTo);
      router.refresh();
    } catch (err) {
      if (err instanceof ApiClientError) {
        setError(
          err.status === 0 || err.message.includes('Failed to fetch')
            ? `Cannot reach platform API at ${getApiBaseUrl()}. Start the API and ensure ENABLE_CLIENT_PORTAL=true.`
            : err.message,
        );
      } else if (err instanceof TypeError) {
        setError(
          `Cannot reach platform API at ${getApiBaseUrl()}. Start apps/api and confirm CORS allows localhost:3100.`,
        );
      } else {
        setError(err instanceof Error ? err.message : 'Sign-in failed.');
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4" noValidate>
      <div className="mb-2 flex items-center gap-3">
        <Image
          src="/brand/logo-icon.png"
          alt=""
          width={44}
          height={44}
          className="h-11 w-11 rounded-brand bg-sand-100 object-contain"
        />
        <div>
          <h1 className="font-sans text-2xl font-semibold text-navy-900 dark:text-white">
            Borrower sign in
          </h1>
          <p className="text-sm text-slate-500 dark:text-white/60">
            Platform portal credentials · same database as staff app
          </p>
        </div>
      </div>

      <div className="rounded-brand border border-gold-500/30 bg-gold-500/10 px-3 py-2 text-xs text-navy-900 dark:text-white/80">
        Uses the Ultimate Credit Repair / Verdin API at <strong>{getApiBaseUrl()}</strong>. Accounts
        are provisioned by staff via Client → Portal user (not self-serve signup).
      </div>

      <div>
        <label htmlFor="email" className="mb-1.5 block text-sm font-medium">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className={inputClass}
          autoComplete="email"
        />
      </div>

      <div>
        <label htmlFor="password" className="mb-1.5 block text-sm font-medium">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={inputClass}
          autoComplete="current-password"
        />
      </div>

      {error ? (
        <p className="text-sm text-critical" role="alert">
          {error}
        </p>
      ) : null}

      <button
        type="submit"
        disabled={loading}
        className={cn(
          'inline-flex w-full items-center justify-center rounded-brand bg-gold-500 px-4 py-3 text-sm font-semibold uppercase tracking-wide text-navy-900 transition hover:bg-gold-400 disabled:opacity-60',
        )}
      >
        {loading ? 'Signing in…' : 'Sign in'}
      </button>

      <div className="flex flex-col gap-2 text-sm">
        <Link href="/contact" className="text-gold-700 hover:underline dark:text-gold-400">
          Need access? Contact your readiness partner
        </Link>
        <Link
          href="/portal/forgot-password"
          className="text-slate-500 hover:underline dark:text-white/50"
        >
          Forgot password?
        </Link>
      </div>
    </form>
  );
}
