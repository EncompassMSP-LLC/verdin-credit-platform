'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { workflowSteps } from '@/lib/crm/data';
import { STAGE_LABELS } from '@/lib/crm/nav';

export default function CrmWorkflowPage() {
  return (
    <RoleGate
      permission="workflow.view"
      fallback={<p className="text-sm text-slate-500">No access to workflow.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Workflow"
        description="Stage SLAs, ownership, and automation density for the lending-readiness journey."
      />
      <ol className="space-y-3">
        {workflowSteps.map((step, index) => (
          <li
            key={step.id}
            className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-[0.65rem] font-semibold uppercase tracking-wider text-gold-600">
                  Step {index + 1} · {STAGE_LABELS[step.stage]}
                </p>
                <h2 className="mt-1 text-lg font-semibold">{step.name}</h2>
                <p className="mt-2 max-w-2xl text-sm text-slate-600 dark:text-white/65">
                  {step.description}
                </p>
              </div>
              <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
                <div>
                  <dt className="text-xs text-slate-500">SLA</dt>
                  <dd className="font-medium">{step.slaDays} days</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate-500">Owner</dt>
                  <dd className="font-medium">{step.ownerRole}</dd>
                </div>
                <div className="col-span-2">
                  <dt className="text-xs text-slate-500">Automations</dt>
                  <dd className="font-medium">{step.automations} rules</dd>
                </div>
              </dl>
            </div>
          </li>
        ))}
      </ol>
    </RoleGate>
  );
}
