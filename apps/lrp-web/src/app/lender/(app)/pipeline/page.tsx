'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { PipelineBoard } from '@/components/lender/PipelineBoard';
import { RoleGate } from '@/components/lender/RoleGate';
import { pipelineCards } from '@/lib/lender/data';

export default function PipelinePage() {
  return (
    <RoleGate permission="pipeline.view">
      <div>
        <PageHeader
          eyebrow="Pipeline"
          title="Borrower pipeline"
          description="Stage visibility for near-miss and in-remediation files. Readiness scores are advisory—underwriting always governs funding decisions."
        />

        <PortalCard
          title="Active stages"
          description="Click a card to open borrower detail. Funded, declined, and withdrawn stages are excluded from the board."
        >
          <PipelineBoard cards={pipelineCards} />
        </PortalCard>
      </div>
    </RoleGate>
  );
}
