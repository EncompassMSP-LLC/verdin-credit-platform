'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { automations } from '@/lib/crm/data';

export default function CrmAutomationsPage() {
  return (
    <RoleGate
      permission="automations.view"
      fallback={<p className="text-sm text-slate-500">No access to automations.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Automations"
        description="Rules engine scaffold. Outbound SMS/email respect quiet hours; no unsupervised dispute filing."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={automations}
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
              cell: (r) => (r.enabled ? 'Enabled' : 'Disabled'),
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
