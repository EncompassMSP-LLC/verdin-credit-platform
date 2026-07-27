'use client';

import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { tasks as seedTasks } from '@/lib/crm/data';
import { useCrmDailyTaskDigest, useCrmTasks } from '@/lib/crm/task-hooks';

type TaskRow = {
  id: string;
  title: string;
  status: string;
  priority: string;
  assigneeName: string;
  relatedType: string;
  relatedName: string;
  dueAt: string | null;
};

export default function CrmTasksPage() {
  const { authMode } = useCrmAuth();
  const isDemo = authMode === 'demo';
  const tasksQuery = useCrmTasks({
    page: 1,
    page_size: 50,
    sort_by: 'due_date',
    sort_order: 'asc',
  });
  const digestQuery = useCrmDailyTaskDigest();

  const rows: TaskRow[] = isDemo
    ? seedTasks.map((t) => ({
        id: t.id,
        title: t.title,
        status: t.status,
        priority: t.priority,
        assigneeName: t.assigneeName,
        relatedType: t.relatedType,
        relatedName: t.relatedName,
        dueAt: t.dueAt,
      }))
    : (tasksQuery.data?.items ?? []).map((t) => ({
        id: t.id,
        title: t.title,
        status: t.status,
        priority: t.priority,
        assigneeName: t.assigned_user_id ? t.assigned_user_id.slice(0, 8) : 'Unassigned',
        relatedType: t.case_id ? 'case' : t.account_id ? 'account' : 'general',
        relatedName: t.case_id ?? t.account_id ?? '—',
        dueAt: t.due_date,
      }));

  const digest = digestQuery.data;

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

      {isDemo ? (
        <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
          Demo mode — showing sample tasks. Sign in with a platform staff account for the live queue
          and daily digest.
        </p>
      ) : null}

      {!isDemo && digest ? (
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {(
            [
              ['Open', digest.counts.open],
              ['Overdue', digest.counts.overdue],
              ['Due today', digest.counts.due_today],
              ['Done today', digest.counts.completed_today],
              ['Assigned to me', digest.counts.assigned_to_me_open],
            ] as const
          ).map(([label, value]) => (
            <div
              key={label}
              className="rounded-md border border-navy-900/10 bg-white px-4 py-3 dark:border-white/10 dark:bg-navy-800"
            >
              <p className="text-xs uppercase tracking-wide text-slate-500">{label}</p>
              <p className="mt-1 text-2xl font-semibold text-navy-900 dark:text-white">{value}</p>
            </div>
          ))}
        </div>
      ) : null}

      {!isDemo && tasksQuery.isLoading ? (
        <p className="mb-4 text-sm text-slate-500">Loading tasks…</p>
      ) : null}
      {!isDemo && tasksQuery.isError ? (
        <p className="mb-4 text-sm text-red-700">
          Could not load tasks. Confirm the API is running and you are signed in.
        </p>
      ) : null}

      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={rows}
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
