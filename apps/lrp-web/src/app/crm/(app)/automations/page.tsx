'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { automations } from '@/lib/crm/data';
import { useCrmAutomationRules, useUpdateCrmAutomationRule } from '@/lib/crm/partner-hooks';
import type { AutomationRule } from '@/lib/crm/types';
import type { CrmAutomationRule } from '@verdin/api-client';

function mapApiRule(row: CrmAutomationRule): AutomationRule {
  return {
    id: row.id,
    name: row.name,
    enabled: row.enabled,
    trigger: row.trigger,
    action: row.action,
    channel: row.channel,
    lastFiredAt: row.last_fired_at,
    fireCount: row.fire_count,
    description: row.description ?? '',
  };
}

export default function CrmAutomationsPage() {
  const { authMode, can } = useCrmAuth();
  const rulesQuery = useCrmAutomationRules();
  const updateRule = useUpdateCrmAutomationRule();

  const liveRows =
    authMode === 'platform' && rulesQuery.data ? rulesQuery.data.map(mapApiRule) : null;
  const rows = liveRows ?? automations;
  const usingDemo = liveRows === null;

  return (
    <RoleGate
      permission="automations.view"
      fallback={<p className="text-sm text-slate-500">No access to automations.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Automations"
        description="Persisted CRM rules (LRP-203). Outbound SMS/email respect quiet hours; no unsupervised dispute filing."
      />
      {usingDemo ? (
        <p className="mb-3 text-xs text-slate-500">
          Showing demo rules — sign in with platform auth to manage persisted automations.
        </p>
      ) : null}
      {rulesQuery.isError ? (
        <p className="mb-3 text-sm text-red-600">Could not load automation rules.</p>
      ) : null}
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={rows}
          columns={[
            {
              key: 'name',
              header: 'Rule',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.name}</p>
                  <p className="text-xs text-slate-500">{r.description}</p>
                </div>
              ),
            },
            {
              key: 'enabled',
              header: 'State',
              cell: (r) =>
                !usingDemo && can('automations.manage') ? (
                  <button
                    type="button"
                    className="text-sm underline decoration-slate-300 underline-offset-2"
                    disabled={updateRule.isPending}
                    onClick={() =>
                      updateRule.mutate({
                        ruleId: r.id,
                        body: { enabled: !r.enabled },
                      })
                    }
                  >
                    {r.enabled ? 'Enabled' : 'Disabled'}
                  </button>
                ) : r.enabled ? (
                  'Enabled'
                ) : (
                  'Disabled'
                ),
            },
            { key: 'trigger', header: 'Trigger', cell: (r) => r.trigger },
            { key: 'channel', header: 'Channel', cell: (r) => r.channel },
            { key: 'action', header: 'Action', cell: (r) => r.action },
            {
              key: 'fires',
              header: 'Fires',
              cell: (r) => String(r.fireCount),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
