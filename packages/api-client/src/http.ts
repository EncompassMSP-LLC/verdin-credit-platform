import type { ApiError } from '@verdin/shared';

const API_PREFIX = '/api/v1';

let configuredBaseUrl: string | null = null;
let accessToken: string | null = null;

export class ApiClientError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
  }
}

export class ApiNotImplementedError extends ApiClientError {
  constructor(endpoint: string) {
    super(`API endpoint not implemented: ${endpoint}`, 501, 'not_implemented');
    this.name = 'ApiNotImplementedError';
  }
}

export interface ApiClientConfig {
  baseUrl?: string;
}

export function configureApiClient(config: ApiClientConfig = {}): void {
  if (config.baseUrl !== undefined) {
    configuredBaseUrl = config.baseUrl.replace(/\/$/, '');
  }
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export function getApiBaseUrl(): string {
  if (configuredBaseUrl !== null) {
    return configuredBaseUrl;
  }

  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '');
  }

  return '';
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  auth?: boolean;
  headers?: Record<string, string>;
}

function formatApiErrorDetail(detail: unknown): string {
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail.map((item) => {
      if (typeof item === 'string') return item;
      if (item && typeof item === 'object') {
        const record = item as { loc?: unknown; msg?: unknown; message?: unknown };
        const loc = Array.isArray(record.loc)
          ? record.loc.filter((p) => p !== 'body').join('.')
          : '';
        const msg =
          typeof record.msg === 'string'
            ? record.msg
            : typeof record.message === 'string'
              ? record.message
              : '';
        if (loc && msg) return `${loc}: ${msg}`;
        if (msg) return msg;
      }
      return null;
    });
    const joined = parts.filter(Boolean).join('; ');
    if (joined) return joined;
  }
  if (detail && typeof detail === 'object') {
    const record = detail as { message?: unknown; msg?: unknown };
    if (typeof record.message === 'string') return record.message;
    if (typeof record.msg === 'string') return record.msg;
    try {
      return JSON.stringify(detail);
    } catch {
      return 'Request failed';
    }
  }
  return 'Request failed';
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true, headers = {} } = options;

  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers,
  };

  if (auth && accessToken) {
    requestHeaders.Authorization = `Bearer ${accessToken}`;
  }

  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;

  const response = await fetch(url, {
    method,
    headers: requestHeaders,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as ApiError & { detail?: unknown };
    throw new ApiClientError(
      formatApiErrorDetail(error.detail) || `HTTP ${response.status}`,
      response.status,
      error.code,
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function uploadRequest<T>(path: string, formData: FormData): Promise<T> {
  const requestHeaders: Record<string, string> = {};
  if (accessToken) {
    requestHeaders.Authorization = `Bearer ${accessToken}`;
  }

  const url = `${getApiBaseUrl()}${path.startsWith('/') ? path : `/${path}`}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: requestHeaders,
    body: formData,
  });

  if (!response.ok) {
    const error = (await response.json().catch(() => ({
      detail: 'Request failed',
    }))) as ApiError & { detail?: unknown };
    throw new ApiClientError(
      formatApiErrorDetail(error.detail) || `HTTP ${response.status}`,
      response.status,
      error.code,
    );
  }

  return response.json() as Promise<T>;
}

export function apiPath(segment: string): string {
  const normalized = segment.startsWith('/') ? segment : `/${segment}`;
  return `${API_PREFIX}${normalized}`;
}

export function notImplemented(endpoint: string): never {
  throw new ApiNotImplementedError(endpoint);
}
