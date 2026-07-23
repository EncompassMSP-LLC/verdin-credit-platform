'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { tasks } from '@/lib/crm/data';

export default function CrmTasksPage() {
  return (
    <RoleGate
      permission="tasks.view"
      fallback={<p className="text-sm text-slate-500">No access to tasks.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Tasks"
        description="CRM work queue aligned to the platform Tasks module (case/client linked)."
      />
      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={tasks}
          columns={[
            { key: 'title', header: 'Task', cell: (r) => r.title },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            { key: 'priority', header: 'Priority', cell: (r) => r.priority },
            { key: 'assignee', header: 'Assignee', cell: (r) => r.assigneeName },
            {
              key: 'related',
              header: 'Related',
              cell: (r) => `${r.relatedType}: ${r.relatedName}`,
            },
            {
              key: 'due',
              header: 'Due',
              cell: (r) => (r.dueAt ? new Date(r.dueAt).toLocaleString() : '—'),
            },
          ]}
        />
      </div>
    </RoleGate>
  );
}
