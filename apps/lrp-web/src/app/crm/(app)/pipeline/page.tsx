'use client';

import { CrmPipelineBoard } from '@/components/crm/CrmPipelineBoard';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { pipelineCards } from '@/lib/crm/data';

export default function CrmPipelinePage() {
  return (
    <RoleGate
      permission="pipeline.view"
      fallback={<p className="text-sm text-slate-500">No access to pipeline.</p>}
    >
      <PageHeader
        eyebrow="Operations"
        title="Pipeline"
        description="Kanban across CRM stages. Partner stages overlay case work on the shared platform."
      />
      <CrmPipelineBoard cards={pipelineCards} />
    </RoleGate>
  );
}
