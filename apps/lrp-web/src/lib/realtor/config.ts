/** Realtor workspace session cookies (LRP-301). */
export const REALTOR_SESSION_COOKIE = 'lrp_realtor_session';
export const REALTOR_SESSION_STORAGE_KEY = 'lrp_realtor_session_v1';
export const REALTOR_SESSION_MAX_AGE_SECONDS = 60 * 60 * 12;

export const REALTOR_ACCESS_COOKIE = 'lrp_realtor_access';
export const REALTOR_REFRESH_COOKIE = 'lrp_realtor_refresh';
export const REALTOR_ACCESS_STORAGE = 'lrp_realtor_access_token';
export const REALTOR_REFRESH_STORAGE = 'lrp_realtor_refresh_token';

export const REALTOR_STAFF_COOKIE_NAMES = {
  accessCookie: REALTOR_ACCESS_COOKIE,
  refreshCookie: REALTOR_REFRESH_COOKIE,
  accessStorage: REALTOR_ACCESS_STORAGE,
  refreshStorage: REALTOR_REFRESH_STORAGE,
  demoSessionCookie: REALTOR_SESSION_COOKIE,
  demoSessionStorage: REALTOR_SESSION_STORAGE_KEY,
} as const;
