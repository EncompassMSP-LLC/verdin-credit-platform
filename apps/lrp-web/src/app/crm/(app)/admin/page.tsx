'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { architectureNotes, DEMO_USERS } from '@/lib/crm/data';
import { ROLE_DEFINITIONS } from '@/lib/crm/permissions';

export default function CrmAdminPage() {
  return (
    <RoleGate
      permission="admin.manage"
      fallback={<p className="text-sm text-slate-500">Admin access required.</p>}
    >
      <PageHeader
        eyebrow="Governance"
        title="Admin"
        description="Organization settings, demo users, and enterprise architecture posture."
      />

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
          <h2 className="text-sm font-semibold">Demo users</h2>
          <ul className="mt-3 space-y-3 text-sm">
            {DEMO_USERS.map((u) => (
              <li
                key={u.id}
                className="flex justify-between gap-3 border-b border-navy-900/8 pb-2 last:border-0 dark:border-white/10"
              >
                <div>
                  <p className="font-medium">{u.displayName}</p>
                  <p className="text-xs text-slate-500">{u.email}</p>
                </div>
                <p className="shrink-0 text-xs text-gold-700 dark:text-gold-400">
                  {ROLE_DEFINITIONS.find((r) => r.role === u.role)?.label}
                </p>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">Password for all demos: changeme123</p>
        </section>

        <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
          <h2 className="text-sm font-semibold">Enterprise architecture</h2>
          <p className="mt-2 text-sm text-slate-600 dark:text-white/65">
            {architectureNotes.edition}
          </p>
          <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Platform maps
          </h3>
          <ul className="mt-2 space-y-1.5 text-sm">
            {Object.entries(architectureNotes.mapsTo).map(([k, v]) => (
              <li key={k}>
                <span className="font-medium capitalize">{k}</span>
                <span className="text-slate-500"> — {v}</span>
              </li>
            ))}
          </ul>
          <h3 className="mt-4 text-xs font-semibold uppercase tracking-wider text-slate-500">
            Explicitly deferred
          </h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600 dark:text-white/65">
            {architectureNotes.deferred.map((d) => (
              <li key={d}>{d}</li>
            ))}
          </ul>
        </section>
      </div>
    </RoleGate>
  );
}
