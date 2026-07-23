import { setAccessToken } from '@verdin/api-client';

const MAX_AGE = 60 * 60 * 24 * 7;

export type StaffRealmCookieNames = {
  accessCookie: string;
  refreshCookie: string;
  accessStorage: string;
  refreshStorage: string;
  /** Legacy demo session cookie (cleared on platform login). */
  demoSessionCookie?: string;
  demoSessionStorage?: string;
};

export function persistStaffSession(
  names: StaffRealmCookieNames,
  accessToken: string,
  refreshToken: string,
) {
  localStorage.setItem(names.accessStorage, accessToken);
  localStorage.setItem(names.refreshStorage, refreshToken);
  document.cookie = `${names.accessCookie}=${encodeURIComponent(accessToken)}; Path=/; Max-Age=${MAX_AGE}; SameSite=Lax`;
  document.cookie = `${names.refreshCookie}=${encodeURIComponent(refreshToken)}; Path=/; Max-Age=${MAX_AGE}; SameSite=Lax`;
  if (names.demoSessionCookie) {
    document.cookie = `${names.demoSessionCookie}=; Path=/; Max-Age=0; SameSite=Lax`;
  }
  if (names.demoSessionStorage) {
    localStorage.removeItem(names.demoSessionStorage);
  }
  setAccessToken(accessToken);
}

export function clearStaffSession(names: StaffRealmCookieNames) {
  localStorage.removeItem(names.accessStorage);
  localStorage.removeItem(names.refreshStorage);
  document.cookie = `${names.accessCookie}=; Path=/; Max-Age=0; SameSite=Lax`;
  document.cookie = `${names.refreshCookie}=; Path=/; Max-Age=0; SameSite=Lax`;
  if (names.demoSessionCookie) {
    document.cookie = `${names.demoSessionCookie}=; Path=/; Max-Age=0; SameSite=Lax`;
  }
  if (names.demoSessionStorage) {
    localStorage.removeItem(names.demoSessionStorage);
  }
  setAccessToken(null);
}

export function readStoredStaffTokens(names: StaffRealmCookieNames): {
  access: string | null;
  refresh: string | null;
} {
  if (typeof window === 'undefined') return { access: null, refresh: null };
  return {
    access: localStorage.getItem(names.accessStorage),
    refresh: localStorage.getItem(names.refreshStorage),
  };
}
