/** Deep-link helpers for dispute / intelligent letter drafts. */

export function accountDisputeLetterPath(accountId: string, letterId: string): string {
  return `/accounts/${accountId}?letter=${encodeURIComponent(letterId)}`;
}

export function caseLetterDraftPath(caseId: string, draftId: string): string {
  return `/cases/${caseId}#letter-draft-builder?draft=${encodeURIComponent(draftId)}`;
}

export function caseLetterDraftBuilderPath(caseId: string): string {
  return `/cases/${caseId}#letter-draft-builder`;
}

export function readAccountLetterIdFromSearch(search: string): string | null {
  const params = new URLSearchParams(search.startsWith('?') ? search.slice(1) : search);
  const letterId = params.get('letter')?.trim();
  return letterId || null;
}

export function readCaseLetterDraftIdFromHash(hash: string): string | null {
  const raw = hash.startsWith('#') ? hash.slice(1) : hash;
  if (!raw.includes('letter-draft-builder')) {
    return null;
  }
  const queryIndex = raw.indexOf('?');
  if (queryIndex === -1) {
    return null;
  }
  const params = new URLSearchParams(raw.slice(queryIndex + 1));
  const draftId = params.get('draft')?.trim();
  return draftId || null;
}
