'use client';

import { useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { DEMO_USERS, orgSettings as seedSettings } from '@/lib/lender/data';
import type { OrgAdminSettings } from '@/lib/lender/types';

export default function AdminPage() {
  const [settings, setSettings] = useState<OrgAdminSettings>({ ...seedSettings });
  const [savedMessage, setSavedMessage] = useState<string | null>(null);

  function updateField<K extends keyof OrgAdminSettings>(key: K, value: OrgAdminSettings[K]) {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSavedMessage(null);
  }

  function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSavedMessage('Settings saved locally for this demo session.');
  }

  return (
    <RoleGate permission="admin.manage">
      <div>
        <PageHeader
          eyebrow="Admin panel"
          title="Organization settings"
          description="Partner configuration for the demo org. Changes are local until Mortgage Partner admin APIs ship."
        />

        <PortalCard title="Partner profile">
          <form onSubmit={onSubmit} className="space-y-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm">
                <span className="font-medium">Organization name</span>
                <input
                  type="text"
                  value={settings.organizationName}
                  onChange={(e) => updateField('organizationName', e.target.value)}
                  className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium">Partner code</span>
                <input
                  type="text"
                  value={settings.partnerCode}
                  onChange={(e) => updateField('partnerCode', e.target.value)}
                  className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium">Branding primary</span>
                <input
                  type="text"
                  value={settings.brandingPrimary}
                  onChange={(e) => updateField('brandingPrimary', e.target.value)}
                  className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                />
              </label>
              <label className="block text-sm">
                <span className="font-medium">Default loan officer</span>
                <select
                  value={settings.defaultLoId}
                  onChange={(e) => updateField('defaultLoId', e.target.value)}
                  className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                >
                  {DEMO_USERS.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.displayName} ({user.title})
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm">
                <span className="font-medium">Retention (days)</span>
                <input
                  type="number"
                  min={30}
                  max={730}
                  value={settings.retentionDays}
                  onChange={(e) => updateField('retentionDays', Number(e.target.value))}
                  className="mt-1.5 w-full rounded-md border border-navy-900/15 bg-white px-3 py-2 text-sm dark:border-white/15 dark:bg-navy-900"
                />
              </label>
            </div>

            <fieldset className="space-y-3 rounded-md border border-navy-900/10 p-4 dark:border-white/10">
              <legend className="px-1 text-sm font-semibold">Notifications & exports</legend>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={settings.readinessExportEnabled}
                  onChange={(e) => updateField('readinessExportEnabled', e.target.checked)}
                  className="rounded border-navy-900/20"
                />
                Enable readiness exports for partner roles
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={settings.notifyOnStageChange}
                  onChange={(e) => updateField('notifyOnStageChange', e.target.checked)}
                  className="rounded border-navy-900/20"
                />
                Notify on pipeline stage change
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={settings.notifyOnReady}
                  onChange={(e) => updateField('notifyOnReady', e.target.checked)}
                  className="rounded border-navy-900/20"
                />
                Notify when borrower reaches advisory lending-ready band
              </label>
            </fieldset>

            <div className="flex flex-wrap items-center gap-3">
              <button
                type="submit"
                className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 dark:bg-gold-500 dark:text-navy-900"
              >
                Save settings
              </button>
              {savedMessage ? (
                <p className="text-sm text-emerald-700 dark:text-emerald-400">{savedMessage}</p>
              ) : null}
            </div>
          </form>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
