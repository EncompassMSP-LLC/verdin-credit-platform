import type { DashboardAi } from '@verdin/api-client';
import { Card } from '@verdin/ui';

interface AiReadinessProps {
  ai: DashboardAi;
}

export function AiReadiness({ ai }: AiReadinessProps) {
  const metrics = [
    { label: 'Documents classified', value: ai.documents_classified },
    { label: 'Metadata extracted', value: ai.metadata_extracted },
    { label: 'Entity resolution rate', value: `${ai.entity_resolution_rate}%` },
    {
      label: 'Average confidence',
      value: ai.average_confidence != null ? `${(ai.average_confidence * 100).toFixed(1)}%` : '—',
    },
    { label: 'AI-ready documents', value: ai.ai_ready_documents },
  ];

  return (
    <Card title="AI Readiness">
      <p className="mb-4 text-sm text-gray-500">Document intelligence pipeline maturity.</p>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {metrics.map((metric) => (
          <div key={metric.label} className="rounded-lg border border-gray-100 bg-gray-50 p-3">
            <p className="text-xs text-gray-500">{metric.label}</p>
            <p className="mt-1 text-xl font-semibold text-gray-900">{metric.value}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
