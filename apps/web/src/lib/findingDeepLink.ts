/** Helpers for Case Dispute Playbook → Case Detail finding deep-links. */

export type FindingPanelAnchor =
  | 'metro2-findings'
  | 'fcra-findings'
  | 'identity-theft-center'
  | 'tradeline-chronology'
  | 'cross-bureau-discrepancies'
  | 'litigation-strength'
  | 'dispute-strategy';

const KIND_TO_ANCHOR: Record<string, FindingPanelAnchor> = {
  metro2: 'metro2-findings',
  fcra: 'fcra-findings',
  identity_theft: 'identity-theft-center',
  chronology: 'tradeline-chronology',
  cross_bureau: 'cross-bureau-discrepancies',
};

export function anchorForSourceKind(sourceKind: string): FindingPanelAnchor {
  return KIND_TO_ANCHOR[sourceKind] ?? 'litigation-strength';
}

export function caseFindingDeepLink(caseId: string, sourceKind: string, sourceId: string): string {
  const anchor = anchorForSourceKind(sourceKind);
  const params = new URLSearchParams({ finding_source: sourceId });
  return `/cases/${caseId}?${params.toString()}#${anchor}`;
}

export interface ParsedFindingSource {
  sourceKind: string;
  bureauOrKey: string;
  ruleId: string;
  index?: number;
  documentId?: string;
  matchKey?: string;
  raw: string;
}

/**
 * Parse litigation-strength `source_id` values.
 * Metro2/FCRA/ID: `{kind}:{bureau}:{rule_id}#{index}@{document_id}`
 * Cross-bureau: `cross_bureau:{match_key}:{discrepancy_type}`
 * Chronology: `chronology:{match_key}:{event_kind}` (approximate)
 */
export function parseFindingSourceId(sourceId: string): ParsedFindingSource | null {
  const raw = sourceId.trim();
  if (!raw) {
    return null;
  }
  const kindSep = raw.indexOf(':');
  if (kindSep < 0) {
    return null;
  }
  const sourceKind = raw.slice(0, kindSep);
  const rest = raw.slice(kindSep + 1);

  if (sourceKind === 'cross_bureau') {
    const parts = rest.split(':');
    const matchKey = parts[0] || undefined;
    return {
      sourceKind,
      bureauOrKey: matchKey ?? 'unknown',
      ruleId: parts.slice(1).join(':') || 'cross_bureau',
      matchKey,
      raw,
    };
  }

  if (sourceKind === 'chronology') {
    const parts = rest.split(':');
    const matchKey = parts[0] || undefined;
    return {
      sourceKind,
      bureauOrKey: matchKey ?? 'unknown',
      ruleId: parts.slice(1).join(':') || 'chronology',
      matchKey,
      raw,
    };
  }

  const atParts = rest.split('@');
  const beforeAt = atParts[0] ?? '';
  const documentId = atParts[1] || undefined;
  const hashParts = beforeAt.split('#');
  const left = hashParts[0] ?? '';
  const indexRaw = hashParts[1];
  const index =
    indexRaw !== undefined && indexRaw !== '' ? Number.parseInt(indexRaw, 10) : undefined;
  const bureauSep = left.indexOf(':');
  const bureauOrKey = bureauSep >= 0 ? left.slice(0, bureauSep) : left;
  const ruleId = bureauSep >= 0 ? left.slice(bureauSep + 1) : left;

  return {
    sourceKind,
    bureauOrKey,
    ruleId,
    index: Number.isFinite(index) ? index : undefined,
    documentId,
    raw,
  };
}

export function findingMatchesSource(
  finding: {
    rule_id: string;
    tradeline_index: number;
    document_id: string;
  },
  sourceId: string | null | undefined,
  expectedKind: 'metro2' | 'fcra' | 'identity_theft',
): boolean {
  if (!sourceId) {
    return false;
  }
  const parsed = parseFindingSourceId(sourceId);
  if (!parsed || parsed.sourceKind !== expectedKind) {
    return false;
  }
  if (parsed.documentId && finding.document_id !== parsed.documentId) {
    return false;
  }
  if (finding.rule_id !== parsed.ruleId) {
    return false;
  }
  if (parsed.index !== undefined && finding.tradeline_index !== parsed.index) {
    return false;
  }
  return true;
}

export function matchKeyFromSource(sourceId: string | null | undefined): string | null {
  if (!sourceId) {
    return null;
  }
  const parsed = parseFindingSourceId(sourceId);
  return parsed?.matchKey ?? null;
}
