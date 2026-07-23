'use client';

import {
  ApiClientError,
  configureApiClient,
  getCurrentUser,
  login as apiLogin,
  refreshToken as apiRefresh,
  setAccessToken,
} from '@verdin/api-client';
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { isDemoAuthEnabled } from '@/lib/auth/realms';
import {
  clearStaffSession,
  persistStaffSession,
  readStoredStaffTokens,
} from '@/lib/auth/staff-session';
import {
  CRM_SESSION_COOKIE,
  CRM_SESSION_MAX_AGE_SECONDS,
  CRM_SESSION_STORAGE_KEY,
  CRM_STAFF_COOKIE_NAMES,
} from '@/lib/crm/config';
import { DEMO_USERS } from '@/lib/crm/data';
import { roleHasPermission } from '@/lib/crm/permissions';
import { mapStaffUserToCrm } from '@/lib/crm/role-map';
import type { CrmPermission, CrmUser } from '@/lib/crm/types';
import { getApiBaseUrl } from '@/lib/platform/config';

type CrmAuthContextValue = {
  user: CrmUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  authMode: 'platform' | 'demo' | null;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => void;
  can: (permission: CrmPermission) => boolean;
};

const CrmAuthContext = createContext<CrmAuthContextValue | null>(null);

function writeDemoCookie(userId: string) {
  document.cookie = `${CRM_SESSION_COOKIE}=${encodeURIComponent(userId)}; Path=/; Max-Age=${CRM_SESSION_MAX_AGE_SECONDS}; SameSite=Lax`;
}

function toPublicDemoUser(user: (typeof DEMO_USERS)[number]): CrmUser {
  return {
    id: user.id,
    email: user.email,
    displayName: user.displayName,
    role: user.role,
    organizationId: user.organizationId,
    organizationName: user.organizationName,
    title: user.title,
  };
}

function readDemoSession(): CrmUser | null {
  try {
    const raw = localStorage.getItem(CRM_SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as CrmUser;
  } catch {
    localStorage.removeItem(CRM_SESSION_STORAGE_KEY);
    return null;
  }
}

function persistDemoSession(user: CrmUser) {
  clearStaffSession(CRM_STAFF_COOKIE_NAMES);
  localStorage.setItem(CRM_SESSION_STORAGE_KEY, JSON.stringify(user));
  writeDemoCookie(user.id);
}

export function CrmAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CrmUser | null>(null);
  const [authMode, setAuthMode] = useState<'platform' | 'demo' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  const logout = useCallback(() => {
    clearStaffSession(CRM_STAFF_COOKIE_NAMES);
    setUser(null);
    setAuthMode(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
    try {
      const tokens = await apiLogin({ email: email.trim(), password });
      persistStaffSession(CRM_STAFF_COOKIE_NAMES, tokens.access_token, tokens.refresh_token);
      const me = await getCurrentUser();
      const mapped = mapStaffUserToCrm(me);
      setUser(mapped);
      setAuthMode('platform');
      return { ok: true as const };
    } catch (err) {
      const platformMessage =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : 'Platform sign-in failed.';

      if (isDemoAuthEnabled('crm')) {
        const match = DEMO_USERS.find(
          (u) => u.email.toLowerCase() === email.trim().toLowerCase() && u.password === password,
        );
        if (match) {
          const publicUser = toPublicDemoUser(match);
          persistDemoSession(publicUser);
          setUser(publicUser);
          setAuthMode('demo');
          return { ok: true as const };
        }
      }

      return {
        ok: false as const,
        error:
          platformMessage.includes('fetch') || platformMessage.includes('Network')
            ? 'Could not reach the API. Use a demo CRM account or start the platform API.'
            : platformMessage || 'Invalid email or password.',
      };
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const { access, refresh } = readStoredStaffTokens(CRM_STAFF_COOKIE_NAMES);

      if (access) {
        setAccessToken(access);
        try {
          const me = await getCurrentUser();
          setUser(mapStaffUserToCrm(me));
          setAuthMode('platform');
          setIsLoading(false);
          return;
        } catch {
          if (refresh) {
            try {
              const tokens = await apiRefresh(refresh);
              persistStaffSession(
                CRM_STAFF_COOKIE_NAMES,
                tokens.access_token,
                tokens.refresh_token,
              );
              const me = await getCurrentUser();
              setUser(mapStaffUserToCrm(me));
              setAuthMode('platform');
              setIsLoading(false);
              return;
            } catch {
              clearStaffSession(CRM_STAFF_COOKIE_NAMES);
            }
          } else {
            clearStaffSession(CRM_STAFF_COOKIE_NAMES);
          }
        }
      }

      const demo = readDemoSession();
      if (demo) {
        writeDemoCookie(demo.id);
        setUser(demo);
        setAuthMode('demo');
      }
      setIsLoading(false);
    };

    void init();
  }, []);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      authMode,
      login,
      logout,
      can: (permission: CrmPermission) => (user ? roleHasPermission(user.role, permission) : false),
    }),
    [user, isLoading, authMode, login, logout],
  );

  return <CrmAuthContext.Provider value={value}>{children}</CrmAuthContext.Provider>;
}

export function useCrmAuth() {
  const ctx = useContext(CrmAuthContext);
  if (!ctx) throw new Error('useCrmAuth must be used within CrmAuthProvider');
  return ctx;
}
