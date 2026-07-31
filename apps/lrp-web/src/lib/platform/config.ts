export const PLATFORM_ACCESS_COOKIE = 'lrp_portal_access';
export const PLATFORM_REFRESH_COOKIE = 'lrp_portal_refresh';
export const PLATFORM_ACCESS_STORAGE = 'lrp_portal_access_token';
export const PLATFORM_REFRESH_STORAGE = 'lrp_portal_refresh_token';

/**
 * Platform API origin for @verdin/api-client.
 * - Prefer NEXT_PUBLIC_API_BASE_URL when set (e.g. https://app.lrpartners.net)
 * - In the browser with no env, use same-origin (empty string) so /api proxies work
 * - Local SSR/dev fallback remains localhost:8000
 */
export function getApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (configured !== undefined && configured.trim() !== '') {
    return configured.replace(/\/$/, '');
  }
  if (typeof window !== 'undefined') {
    return '';
  }
  if (process.env.NODE_ENV === 'production') {
    return '';
  }
  return 'http://localhost:8000';
}
