import type { UserRole } from '@verdin/shared';

import { apiPath, request } from './http';

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  is_active: boolean;
  organization_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  return request<TokenResponse>(apiPath('/auth/login'), {
    method: 'POST',
    body: credentials,
    auth: false,
  });
}

export async function refreshToken(refreshTokenValue: string): Promise<TokenResponse> {
  return request<TokenResponse>(apiPath('/auth/refresh'), {
    method: 'POST',
    body: { refresh_token: refreshTokenValue } satisfies RefreshTokenRequest,
    auth: false,
  });
}

export async function getCurrentUser(): Promise<User> {
  return request<User>(apiPath('/auth/me'));
}
