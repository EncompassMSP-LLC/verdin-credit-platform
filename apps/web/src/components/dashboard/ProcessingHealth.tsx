import type { DashboardProcessing } from '@verdin/api-client';
import { Card } from '@verdin/ui';

interface ProcessingHealthProps {
  processing: DashboardProcessing;
}

const STAGES = [
  { key: 'uploads_today' as const, label: 'Uploads Today' },
  { key: 'ocr_running' as const, label: 'OCR Running' },
  { key: 'ocr_failed' as const, label: 'OCR Failed', alert: true },
  { key: 'classification_pending' as const, label: 'Classification Pending' },
  { key: 'metadata_pending' as const, label: 'Metadata Pending' },
  { key: 'entity_resolution_pending' as const, label: 'Entity Resolution Pending' },
];

export function ProcessingHealth({ processing }: ProcessingHealthProps) {
  return (
    <Card title="Processing Health">
      <p className="mb-4 text-sm text-gray-500">Live document pipeline status.</p>
      <div className="space-y-3">
        {STAGES.map((stage, index) => {
          const count = processing[stage.key];
          const isAlert = stage.alert && count > 0;

          return (
            <div key={stage.key} className="flex items-center gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600">
                {index + 1}
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-sm font-medium text-gray-900">{stage.label}</span>
                  <span
                    className={`text-sm font-semibold tabular-nums ${
                      isAlert ? 'text-red-600' : 'text-gray-700'
                    }`}
                  >
                    {count}
                  </span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-gray-100">
                  <div
                    className={`h-full rounded-full transition-all ${
                      isAlert ? 'bg-red-500' : 'bg-brand-500'
                    }`}
                    style={{ width: count > 0 ? '100%' : '0%' }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
