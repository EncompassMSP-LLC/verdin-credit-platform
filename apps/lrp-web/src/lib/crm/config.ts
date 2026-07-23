/** Demo CRM session cookie (legacy local auth). */
export const CRM_SESSION_COOKIE = 'lrp_crm_session';
export const CRM_SESSION_STORAGE_KEY = 'lrp_crm_session_v1';
export const CRM_SESSION_MAX_AGE_SECONDS = 60 * 60 * 12;

/** Platform staff JWT cookies for CRM realm (Epic E1). */
export const CRM_ACCESS_COOKIE = 'lrp_crm_access';
export const CRM_REFRESH_COOKIE = 'lrp_crm_refresh';
export const CRM_ACCESS_STORAGE = 'lrp_crm_access_token';
export const CRM_REFRESH_STORAGE = 'lrp_crm_refresh_token';

export const CRM_STAFF_COOKIE_NAMES = {
  accessCookie: CRM_ACCESS_COOKIE,
  refreshCookie: CRM_REFRESH_COOKIE,
  accessStorage: CRM_ACCESS_STORAGE,
  refreshStorage: CRM_REFRESH_STORAGE,
  demoSessionCookie: CRM_SESSION_COOKIE,
  demoSessionStorage: CRM_SESSION_STORAGE_KEY,
} as const;
