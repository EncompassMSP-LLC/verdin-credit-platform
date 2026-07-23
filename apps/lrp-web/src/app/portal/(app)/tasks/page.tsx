'use client';

import { useMemo, useState } from 'react';
import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import { usePrimaryCase } from '@/lib/platform/hooks';
import { usePortalChecklist, useUpdatePortalChecklistItem } from '@/lib/platform/readiness-hooks';
import { formatDate } from '@/lib/utils';

export default function TasksPage() {
  const { primary } = usePrimaryCase();
  const checklistQuery = usePortalChecklist(primary?.id);
  const updateMutation = useUpdatePortalChecklistItem(primary?.id);
  const [filter, setFilter] = useState<'all' | 'open' | 'done'>('open');

  const visible = useMemo(() => {
    const items = checklistQuery.data ?? [];
    if (filter === 'all') return items;
    return items.filter((task) => task.status === filter);
  }, [filter, checklistQuery.data]);

  function toggle(id: string, status: 'open' | 'done') {
    updateMutation.mutate({
      itemId: id,
      status: status === 'done' ? 'open' : 'done',
    });
  }

  return (
    <div>
      <PageHeader
        eyebrow="Tasks"
        title="Your action plan"
        description="Complete these tasks to move your readiness forward. Due dates are set by your advisor (not editable here)."
      />

      {!primary ? (
        <p className="rounded-brand border border-navy-900/10 bg-sand-50 px-4 py-3 text-sm text-slate-600 dark:border-white/10 dark:bg-navy-900/40 dark:text-white/70">
          Link a case to your client record to view your checklist.
        </p>
      ) : (
        <>
          <div className="mb-4 flex flex-wrap gap-2">
            {(['open', 'done', 'all'] as const).map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setFilter(value)}
                className={
                  filter === value
                    ? 'rounded-brand bg-navy-900 px-3 py-1.5 text-sm font-medium text-white dark:bg-gold-500 dark:text-navy-900'
                    : 'rounded-brand border border-navy-900/10 bg-white px-3 py-1.5 text-sm dark:border-white/10 dark:bg-navy-800'
                }
              >
                {value[0].toUpperCase() + value.slice(1)}
              </button>
            ))}
          </div>

          <PortalCard>
            {checklistQuery.isLoading ? (
              <p className="text-sm text-slate-500">Loading checklist…</p>
            ) : checklistQuery.isError ? (
              <p className="text-sm text-critical">
                Could not load checklist from the platform API.
              </p>
            ) : visible.length === 0 ? (
              <p className="text-sm text-slate-500 dark:text-white/65">No items in this filter.</p>
            ) : (
              <ul className="divide-y divide-navy-900/8 dark:divide-white/10">
                {visible.map((task) => (
                  <li
                    key={task.id}
                    className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="flex items-start gap-3">
                      <input
                        type="checkbox"
                        checked={task.status === 'done'}
                        disabled={updateMutation.isPending}
                        onChange={() => toggle(task.id, task.status)}
                        className="mt-1 h-4 w-4 rounded border-navy-900/30 text-gold-500 focus:ring-gold-500"
                        aria-label={`Mark ${task.title} as ${task.status === 'done' ? 'open' : 'done'}`}
                      />
                      <div>
                        <p
                          className={
                            task.status === 'done'
                              ? 'font-medium text-slate-400 line-through'
                              : 'font-medium text-navy-900 dark:text-white'
                          }
                        >
                          {task.title}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-white/55">
                          {task.category}
                          {task.due_date ? ` · Due ${formatDate(task.due_date)}` : null}
                        </p>
                      </div>
                    </div>
                    <StatusPill
                      tone={
                        task.status === 'done'
                          ? 'good'
                          : task.priority === 'high'
                            ? 'warn'
                            : 'neutral'
                      }
                    >
                      {task.status === 'done' ? 'Done' : task.priority}
                    </StatusPill>
                  </li>
                ))}
              </ul>
            )}
          </PortalCard>
        </>
      )}
    </div>
  );
}
