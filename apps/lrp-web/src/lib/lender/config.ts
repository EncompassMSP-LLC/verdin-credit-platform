/** Demo lender session cookie (local auth / partner JWT deferred). */
export const LENDER_SESSION_COOKIE = 'lrp_lender_session';
export const LENDER_SESSION_STORAGE_KEY = 'lrp_lender_session_v1';
export const LENDER_SESSION_MAX_AGE_SECONDS = 60 * 60 * 12;

/** Platform staff JWT cookies for lender realm interim (Epic E1). */
export const LENDER_ACCESS_COOKIE = 'lrp_lender_access';
export const LENDER_REFRESH_COOKIE = 'lrp_lender_refresh';
export const LENDER_ACCESS_STORAGE = 'lrp_lender_access_token';
export const LENDER_REFRESH_STORAGE = 'lrp_lender_refresh_token';

export const LENDER_STAFF_COOKIE_NAMES = {
  accessCookie: LENDER_ACCESS_COOKIE,
  refreshCookie: LENDER_REFRESH_COOKIE,
  accessStorage: LENDER_ACCESS_STORAGE,
  refreshStorage: LENDER_REFRESH_STORAGE,
  demoSessionCookie: LENDER_SESSION_COOKIE,
  demoSessionStorage: LENDER_SESSION_STORAGE_KEY,
} as const;
