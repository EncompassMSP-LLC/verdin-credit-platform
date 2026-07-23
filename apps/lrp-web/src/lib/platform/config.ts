export const PLATFORM_ACCESS_COOKIE = 'lrp_portal_access';
export const PLATFORM_REFRESH_COOKIE = 'lrp_portal_refresh';
export const PLATFORM_ACCESS_STORAGE = 'lrp_portal_access_token';
export const PLATFORM_REFRESH_STORAGE = 'lrp_portal_refresh_token';

export function getApiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000').replace(/\/$/, '');
}
