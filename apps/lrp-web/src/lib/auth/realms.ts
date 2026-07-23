/**
 * LRP auth realms — Vol 24 / Epic E1
 *
 * | Realm    | Audience              | Token source                                      |
 * | -------- | --------------------- | ------------------------------------------------- |
 * | portal   | Borrower / client     | Platform portal JWT (`/portal/auth/*`)            |
 * | crm      | Staff operators       | Platform staff JWT (`/auth/*`)                    |
 * | lender   | LO / partner users    | Staff JWT (interim) or demo; partner JWT deferred |
 *
 * Cookies are realm-scoped so middleware can gate routes independently.
 * `@verdin/api-client` holds one in-memory access token per tab — each
 * provider calls `setAccessToken` on init / login for its realm.
 */

export type LrpAuthRealm = 'portal' | 'crm' | 'lender';

export const AUTH_REALM_LABELS: Record<LrpAuthRealm, string> = {
  portal: 'Borrower portal',
  crm: 'Enterprise CRM',
  lender: 'Lender workspace',
};

/** When true, CRM/lender accept local demo users if platform login fails. */
export function isDemoAuthEnabled(realm: 'crm' | 'lender'): boolean {
  const key =
    realm === 'crm' ? 'NEXT_PUBLIC_LRP_CRM_DEMO_AUTH' : 'NEXT_PUBLIC_LRP_LENDER_DEMO_AUTH';
  const raw = process.env[key];
  if (raw === undefined || raw === '') return true;
  return raw !== '0' && raw.toLowerCase() !== 'false';
}
