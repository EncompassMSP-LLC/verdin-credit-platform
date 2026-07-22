'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard, StatusPill } from '@/components/portal/PortalCard';
import {
  usePortalLearningModules,
  useTogglePortalLearningModule,
} from '@/lib/platform/readiness-hooks';

export default function LearningPage() {
  const modulesQuery = usePortalLearningModules();
  const toggleMutation = useTogglePortalLearningModule();
  const modules = modulesQuery.data ?? [];

  return (
    <div>
      <PageHeader
        eyebrow="Learning Center"
        title="Education that protects dignity"
        description="Short modules that explain readiness without shame narratives or miracle claims. Completion syncs to your portal account."
      />

      {modulesQuery.isLoading ? (
        <p className="text-sm text-slate-500">Loading modules…</p>
      ) : modulesQuery.isError ? (
        <p className="rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          Could not load learning modules from the platform API.
        </p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {modules.map((module) => (
            <PortalCard key={module.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-eyebrow text-slate-500">
                    {module.level}
                  </p>
                  <h2 className="mt-1 text-lg font-semibold text-navy-900 dark:text-white">
                    {module.title}
                  </h2>
                  <p className="mt-2 text-sm text-slate-500 dark:text-white/60">
                    {module.minutes} min · Self-paced
                  </p>
                  <p className="mt-3 text-sm text-slate-500 dark:text-white/65">{module.summary}</p>
                </div>
                <StatusPill tone={module.completed ? 'good' : 'neutral'}>
                  {module.completed ? 'Completed' : 'Not started'}
                </StatusPill>
              </div>
              <button
                type="button"
                disabled={toggleMutation.isPending}
                onClick={() => toggleMutation.mutate(module)}
                className="mt-5 rounded-brand border border-navy-900/15 px-3 py-2 text-sm font-medium hover:bg-sand-50 dark:border-white/15 dark:hover:bg-navy-900/50"
              >
                {module.completed ? 'Mark as not started' : 'Mark complete'}
              </button>
            </PortalCard>
          ))}
        </div>
      )}
    </div>
  );
}
