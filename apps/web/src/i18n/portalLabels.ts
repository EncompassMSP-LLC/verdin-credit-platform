/** Helpers for translating portal enum-like status values. */
export function translatePortalKey(
  t: (key: string) => string,
  namespace: 'status' | 'stage' | 'disputeStatus',
  value: string,
): string {
  const key = `${namespace}.${value}`;
  const translated = t(key);
  if (translated === key) {
    return value.replaceAll('_', ' ');
  }
  return translated;
}
