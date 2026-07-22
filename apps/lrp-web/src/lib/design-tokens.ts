/**
 * Design / product enums aligned to Build Bible.
 * Vol 22 · STAGE-MODEL · FOUNDER-REVIEW P0-2 / P0-3
 */

export const READINESS_BANDS = ['building', 'progressing', 'near_ready', 'lending_ready'] as const;

export type ReadinessBand = (typeof READINESS_BANDS)[number];

export const READINESS_BAND_LABELS: Record<ReadinessBand, string> = {
  building: 'Building',
  progressing: 'Progressing',
  near_ready: 'Near ready',
  lending_ready: 'Lending Ready',
};

/** Tailwind-friendly class hints for band badges */
export const READINESS_BAND_CLASSES: Record<ReadinessBand, string> = {
  building: 'bg-slate-500/15 text-slate-600',
  progressing: 'bg-gold-600/15 text-gold-700',
  near_ready: 'bg-gold-500/20 text-gold-700',
  lending_ready: 'bg-gold-700/15 text-gold-700',
};

export const CASE_STAGES = [
  'intake',
  'documenting',
  'analyzing',
  'planning',
  'remediating',
  'near_ready',
  'lending_ready',
  'paused',
  'closed',
] as const;

export type CaseStage = (typeof CASE_STAGES)[number];

export const CASE_STAGE_LABELS: Record<CaseStage, string> = {
  intake: 'Intake',
  documenting: 'Documenting',
  analyzing: 'Analyzing',
  planning: 'Planning',
  remediating: 'Remediating',
  near_ready: 'Near ready',
  lending_ready: 'Lending Ready',
  paused: 'Paused',
  closed: 'Closed',
};

export const ADVISORY_DISCLAIMER_SHORT =
  'Lending Readiness Score™ is advisory and not a loan approval or underwriting decision.';

export const ADVISORY_DISCLAIMER_LONG =
  'Lending Readiness Score™ is an advisory tool for organizing credit and documentation work toward a mortgage conversation. It is not a credit score from a consumer reporting agency, not an underwriting decision, and not a guarantee of loan approval or terms.';
