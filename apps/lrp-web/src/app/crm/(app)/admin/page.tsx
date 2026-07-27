'use client';

import { useState } from 'react';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { architectureNotes, DEMO_USERS } from '@/lib/crm/data';
import {
  useCanShowDemoActions,
  useGenerateSampleBorrowers,
  useOrganizationContext,
} from '@/lib/crm/org-context-hooks';
import { ROLE_DEFINITIONS } from '@/lib/crm/permissions';
import { useCrmAuth } from '@/lib/crm/auth';

export default function CrmAdminPage() {
  const { authMode } = useCrmAuth();
  const showDemoActions = useCanShowDemoActions();
  const orgContextQuery = useOrganizationContext();
  const sampleMutation = useGenerateSampleBorrowers();
  const [sampleMessage, setSampleMessage] = useState<string | null>(null);

  const orgType = orgContextQuery.data?.organization_type;
  const isProductionOrg = orgType === 'production';

  return (
    <RoleGate
      permission="admin.manage"
      fallback={<p className="text-sm text-slate-500">Admin access required.</p>}
    >
      <PageHeader
        eyebrow="Governance"
        title="Admin"
        description="Organization settings, demo tools (non-production only), and enterprise architecture posture."
      />

      {orgContextQuery.data ? (
        <p className="mb-4 text-sm text-slate-600 dark:text-white/65">
          Organization type: <span className="font-medium uppercase tracking-wide">{orgType}</span>
          {isProductionOrg ? ' — demo actions are disabled for production organizations.' : null}
        </p>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        {showDemoActions && !isProductionOrg ? (
          <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
            <h2 className="text-sm font-semibold">Demo tools</h2>
            <p className="mt-2 text-xs text-slate-500">
              Visible only when organization type is not PRODUCTION and demo feature flags are
              enabled. Never shown for live production orgs.
            </p>
            {authMode === 'demo' ? (
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
            ) : null}
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                type="button"
                disabled={sampleMutation.isPending || authMode === 'demo'}
                onClick={() => {
                  setSampleMessage(null);
                  sampleMutation.mutate(3, {
                    onSuccess: (result) => {
                      setSampleMessage(
                        `Created ${result.created_client_ids.length} sample borrowers.`,
                      );
                    },
                    onError: () => {
                      setSampleMessage(
                        'Could not generate sample borrowers (blocked or unavailable).',
                      );
                    },
                  });
                }}
                className="rounded-md bg-navy-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
              >
                Generate Demo Data
              </button>
              <button
                type="button"
                disabled
                title="Reset is only available via dedicated demo seed scripts"
                className="rounded-md border border-navy-900/20 px-3 py-1.5 text-sm text-slate-400"
              >
                Reset Workspace
              </button>
            </div>
            {authMode === 'demo' ? (
              <p className="mt-3 text-xs text-slate-500">
                Local demo session — use seed scripts or sign in with a DEMO organization to create
                live sample borrowers. Password for demo users: changeme123
              </p>
            ) : null}
            {sampleMessage ? <p className="mt-2 text-xs text-slate-600">{sampleMessage}</p> : null}
          </section>
        ) : (
          <section className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800">
            <h2 className="text-sm font-semibold">Demo tools</h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-white/65">
              Generate Demo Data, Load Example Client, Reset Workspace, and Populate Samples are
              hidden for production organizations.
            </p>
          </section>
        )}

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
