/**
 * LRP auth realms — Vol 24 / Epic E1
 *
 * | Realm    | Audience              | Token source                                      |
 * | -------- | --------------------- | ------------------------------------------------- |
 * | portal   | Borrower / client     | Platform portal JWT (`/portal/auth/*`)            |
 * | crm      | Staff operators       | Platform staff JWT (`/auth/*`)                    |
 * | lender   | LO / partner users    | Staff JWT (interim); partner JWT deferred         |
 *
 * Cookies are realm-scoped so middleware can gate routes independently.
 * `@verdin/api-client` holds one in-memory access token per tab — each
 * provider calls `setAccessToken` on init / login for its realm.
 *
 * Demo auth (LRP-108): local/dev fallback only. Always disabled in
 * production builds so production orgs cannot use seed credentials.
 */

export type LrpAuthRealm = 'portal' | 'crm' | 'lender';

export const AUTH_REALM_LABELS: Record<LrpAuthRealm, string> = {
  portal: 'Borrower portal',
  crm: 'Enterprise CRM',
  lender: 'Lender workspace',
};

/**
 * Resolve whether CRM/lender demo credential fallback is allowed.
 * Pure helper for tests and env evaluation.
 *
 * Rules (LRP-108 / LRP-109):
 * - Production builds (`nodeEnv === 'production'`): always false
 * - Global `enableDemoLogin` false/0 → false (maps to ENABLE_DEMO_LOGIN)
 * - Otherwise: realm env unset/empty → true (local DX); explicit false/0 → false
 */
export function resolveDemoAuthEnabled(options: {
  nodeEnv: string | undefined;
  envValue: string | undefined;
  enableDemoLogin?: string | undefined;
}): boolean {
  if (options.nodeEnv === 'production') return false;
  const globalGate = options.enableDemoLogin;
  if (globalGate !== undefined && globalGate !== '') {
    if (globalGate === '0' || globalGate.toLowerCase() === 'false') return false;
  }
  const raw = options.envValue;
  if (raw === undefined || raw === '') return true;
  return raw !== '0' && raw.toLowerCase() !== 'false';
}

/** When true, CRM/lender accept local demo users if platform login fails. */
export function isDemoAuthEnabled(realm: 'crm' | 'lender'): boolean {
  const key =
    realm === 'crm' ? 'NEXT_PUBLIC_LRP_CRM_DEMO_AUTH' : 'NEXT_PUBLIC_LRP_LENDER_DEMO_AUTH';
  return resolveDemoAuthEnabled({
    nodeEnv: process.env.NODE_ENV,
    envValue: process.env[key],
    enableDemoLogin: process.env.NEXT_PUBLIC_ENABLE_DEMO_LOGIN,
  });
}
