'use client';

import { useTheme } from 'next-themes';
import { useState, useSyncExternalStore } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { getApiBaseUrl } from '@/lib/platform/config';

function useMounted() {
  return useSyncExternalStore(
    () => () => {},
    () => true,
    () => false,
  );
}

export default function SettingsPage() {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const mounted = useMounted();
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(false);

  return (
    <div>
      <PageHeader
        eyebrow="Settings"
        title="Portal preferences"
        description="Appearance and local notification preferences. Auth is issued by the platform API."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <PortalCard title="Appearance">
          <p className="text-sm text-slate-500 dark:text-white/60">
            Current theme: {mounted ? resolvedTheme : '…'}
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {(['light', 'dark', 'system'] as const).map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setTheme(value)}
                className={
                  theme === value
                    ? 'rounded-brand bg-navy-900 px-3 py-2 text-sm font-medium text-white dark:bg-gold-500 dark:text-navy-900'
                    : 'rounded-brand border border-navy-900/15 px-3 py-2 text-sm dark:border-white/15'
                }
              >
                {value[0].toUpperCase() + value.slice(1)}
              </button>
            ))}
          </div>
        </PortalCard>

        <PortalCard title="Platform connection">
          <dl className="space-y-3 text-sm">
            <div>
              <dt className="text-slate-500">API base URL</dt>
              <dd className="mt-1 font-mono text-xs">{getApiBaseUrl()}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Auth</dt>
              <dd className="mt-1 font-medium">Portal JWT via /portal/auth/*</dd>
            </div>
            <div>
              <dt className="text-slate-500">Database</dt>
              <dd className="mt-1 font-medium">
                Shared Postgres (client_portal_users, cases, documents, messaging)
              </dd>
            </div>
          </dl>
        </PortalCard>

        <PortalCard title="Local notification prefs">
          <ul className="space-y-4">
            {(
              [
                ['emailAlerts', 'Email alerts', emailAlerts, setEmailAlerts],
                ['smsAlerts', 'SMS alerts', smsAlerts, setSmsAlerts],
              ] as const
            ).map(([id, label, value, setter]) => (
              <li key={id} className="flex items-center justify-between gap-3">
                <label htmlFor={id} className="text-sm font-medium">
                  {label}
                </label>
                <input
                  id={id}
                  type="checkbox"
                  checked={value}
                  onChange={(e) => setter(e.target.checked)}
                  className="h-4 w-4 rounded border-navy-900/30 text-gold-500 focus:ring-gold-500"
                />
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">
            Stored locally in this browser until portal notification preferences are exposed on the
            API.
          </p>
        </PortalCard>

        <PortalCard title="Privacy">
          <p className="text-sm text-slate-500 dark:text-white/65">
            Your session uses the same tenant-scoped portal realm as the staff-provisioned client
            portal. Data is not stored in a separate Supabase project.
          </p>
        </PortalCard>
      </div>
    </div>
  );
}
