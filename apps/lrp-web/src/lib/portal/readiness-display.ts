import {
  ADVISORY_DISCLAIMER_SHORT,
  CASE_STAGE_LABELS,
  READINESS_BAND_CLASSES,
  READINESS_BAND_LABELS,
  type CaseStage,
  type ReadinessBand,
} from '@/lib/design-tokens';

export { ADVISORY_DISCLAIMER_SHORT };

/** Normalize API band strings to canonical Vol 22 bands. */
export function normalizeReadinessBand(raw: string | null | undefined): ReadinessBand | null {
  if (!raw) return null;
  const key = raw.trim().toLowerCase().replace(/\s+/g, '_').replace(/-/g, '_');
  const aliases: Record<string, ReadinessBand> = {
    building: 'building',
    progressing: 'progressing',
    near_ready: 'near_ready',
    nearready: 'near_ready',
    lending_ready: 'lending_ready',
    lendingready: 'lending_ready',
    mortgage_ready: 'lending_ready',
    ready: 'lending_ready',
  };
  return aliases[key] ?? null;
}

export function readinessBandLabel(raw: string | null | undefined): string {
  const band = normalizeReadinessBand(raw);
  if (band) return READINESS_BAND_LABELS[band];
  return raw?.trim() || 'Pending';
}

export function readinessBandClass(raw: string | null | undefined): string {
  const band = normalizeReadinessBand(raw);
  if (band) return READINESS_BAND_CLASSES[band];
  return 'bg-slate-500/10 text-slate-500';
}

export function caseStageLabel(stage: string | null | undefined): string {
  if (!stage) return '—';
  const key = stage as CaseStage;
  if (key in CASE_STAGE_LABELS) return CASE_STAGE_LABELS[key];
  // Legacy platform case stages
  const legacy: Record<string, string> = {
    review: 'Analyzing',
    evidence_gathering: 'Documenting',
    dispute_preparation: 'Remediating',
    awaiting_response: 'Remediating',
    monitoring: 'Near ready',
    complete: 'Lending Ready',
  };
  return legacy[stage] ?? stage.replace(/_/g, ' ');
}
