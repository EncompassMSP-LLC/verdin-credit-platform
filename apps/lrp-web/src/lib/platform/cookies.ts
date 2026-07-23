import { PLATFORM_ACCESS_COOKIE, PLATFORM_REFRESH_COOKIE } from '@/lib/platform/config';

export function setAuthCookies(accessToken: string, refreshToken: string) {
  const maxAge = 60 * 60 * 24 * 7;
  document.cookie = `${PLATFORM_ACCESS_COOKIE}=${encodeURIComponent(accessToken)}; Path=/; Max-Age=${maxAge}; SameSite=Lax`;
  document.cookie = `${PLATFORM_REFRESH_COOKIE}=${encodeURIComponent(refreshToken)}; Path=/; Max-Age=${maxAge}; SameSite=Lax`;
}

export function clearAuthCookies() {
  document.cookie = `${PLATFORM_ACCESS_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
  document.cookie = `${PLATFORM_REFRESH_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}
