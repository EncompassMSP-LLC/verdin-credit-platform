'use client';

import {
  acceptRealtorInvite,
  configureApiClient,
  previewRealtorInvite,
  type RealtorInvitePreview,
} from '@verdin/api-client';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useRealtorAuth } from '@/lib/realtor/auth';
import { getApiBaseUrl } from '@/lib/platform/config';

export function RealtorActivateForm() {
  const router = useRouter();
  const search = useSearchParams();
  const { applySessionTokens } = useRealtorAuth();
  const [token, setToken] = useState(search.get('token') || '');
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [preview, setPreview] = useState<RealtorInvitePreview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const [previewPending, setPreviewPending] = useState(false);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  async function loadPreview() {
    if (token.trim().length < 16) {
      setError('Invite token looks too short.');
      return;
    }
    setPreviewPending(true);
    setError(null);
    try {
      const data = await previewRealtorInvite(token.trim());
      setPreview(data);
    } catch (err) {
      setPreview(null);
      setError(err instanceof Error ? err.message : 'Invalid invite token.');
    } finally {
      setPreviewPending(false);
    }
  }

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setPending(true);
    setError(null);
    try {
      const result = await acceptRealtorInvite(token.trim(), password);
      applySessionTokens(result.access_token, result.refresh_token, result.realtor);
      router.replace('/realtor/dashboard');
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Activation failed.');
    } finally {
      setPending(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label htmlFor="invite-token" className="block text-sm font-medium">
          Invite token
        </label>
        <div className="mt-1.5 flex gap-2">
          <input
            id="invite-token"
            required
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
          />
          <button
            type="button"
            onClick={() => void loadPreview()}
            disabled={previewPending}
            className="shrink-0 rounded-md border border-lrp-border px-3 py-2 text-sm font-medium text-navy-900 hover:bg-lrp-surface disabled:opacity-60"
          >
            {previewPending ? '…' : 'Preview'}
          </button>
        </div>
      </div>
      {preview ? (
        <p className="rounded-md border border-lrp-border bg-lrp-surface px-3 py-2 text-sm text-slate-600">
          Welcome {preview.first_name} — {preview.partnership_display_name} (
          {preview.partner_organization_name})
          {preview.already_accepted ? ' · already accepted' : null}
        </p>
      ) : null}
      <div>
        <label htmlFor="activate-password" className="block text-sm font-medium">
          Choose password
        </label>
        <input
          id="activate-password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      <div>
        <label htmlFor="activate-confirm" className="block text-sm font-medium">
          Confirm password
        </label>
        <input
          id="activate-confirm"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
          className="mt-1.5 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2.5 text-sm"
        />
      </div>
      {error ? (
        <p className="rounded-md border border-critical/30 bg-critical/10 px-3 py-2 text-sm text-critical">
          {error}
        </p>
      ) : null}
      <button
        type="submit"
        disabled={pending || Boolean(preview?.already_accepted)}
        className="w-full rounded-md bg-navy-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60"
      >
        {pending ? 'Activating…' : 'Activate account'}
      </button>
      <Link
        href="/realtor/login"
        className="inline-block text-sm font-medium text-gold-700 hover:underline"
      >
        ← Back to sign in
      </Link>
    </form>
  );
}
