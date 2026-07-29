'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { automations } from '@/lib/crm/data';
import {
  useCrmAutomationAuditEvents,
  useCrmAutomationRules,
  useFireCrmAutomationRule,
  useUpdateCrmAutomationRule,
} from '@/lib/crm/partner-hooks';
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
  const eventsQuery = useCrmAutomationAuditEvents(20);
  const updateRule = useUpdateCrmAutomationRule();
  const fireRule = useFireCrmAutomationRule();

  const liveRows =
    authMode === 'platform' && rulesQuery.data ? rulesQuery.data.map(mapApiRule) : null;
  const rows = liveRows ?? automations;
  const usingDemo = liveRows === null;
  const auditRows = !usingDemo && eventsQuery.data ? eventsQuery.data : [];

  return (
    <RoleGate
      permission="automations.view"
      fallback={<p className="text-sm text-slate-500">No access to automations.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Automations"
        description="Persisted CRM rules with durable audit events (LRP-502). Dry-run by default; no unsupervised dispute filing."
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
            {
              key: 'test',
              header: 'Test',
              cell: (r) =>
                !usingDemo && can('automations.manage') ? (
                  <button
                    type="button"
                    className="text-sm text-navy-800 underline decoration-slate-300 underline-offset-2 dark:text-slate-200"
                    disabled={fireRule.isPending}
                    onClick={() =>
                      fireRule.mutate({
                        ruleId: r.id,
                        body: { dry_run: true },
                      })
                    }
                  >
                    Dry-run
                  </button>
                ) : (
                  '—'
                ),
            },
          ]}
        />
      </div>

      {!usingDemo ? (
        <div className="mt-8">
          <h2 className="mb-2 text-sm font-semibold text-navy-900 dark:text-white">
            Recent audit events
          </h2>
          {eventsQuery.isError ? (
            <p className="mb-3 text-sm text-red-600">Could not load automation audit events.</p>
          ) : null}
          <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
            <DataTable
              rows={auditRows}
              columns={[
                {
                  key: 'started_at',
                  header: 'When',
                  cell: (e) => new Date(e.started_at).toLocaleString(),
                },
                { key: 'event_kind', header: 'Event', cell: (e) => e.event_kind },
                { key: 'status', header: 'Status', cell: (e) => e.status },
                { key: 'channel', header: 'Channel', cell: (e) => e.channel ?? '—' },
                {
                  key: 'rule',
                  header: 'Rule',
                  cell: (e) => (e.rule_id ? e.rule_id.slice(0, 8) : '—'),
                },
              ]}
            />
          </div>
        </div>
      ) : null}
    </RoleGate>
  );
}
