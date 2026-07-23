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
  LENDER_SESSION_COOKIE,
  LENDER_SESSION_MAX_AGE_SECONDS,
  LENDER_SESSION_STORAGE_KEY,
  LENDER_STAFF_COOKIE_NAMES,
} from '@/lib/lender/config';
import { DEMO_USERS } from '@/lib/lender/data';
import { roleHasPermission } from '@/lib/lender/permissions';
import { mapStaffUserToLender } from '@/lib/lender/role-map';
import type { LenderPermission, LenderUser } from '@/lib/lender/types';
import { getApiBaseUrl } from '@/lib/platform/config';

type LenderAuthContextValue = {
  user: LenderUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  authMode: 'platform' | 'demo' | null;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => void;
  can: (permission: LenderPermission) => boolean;
};

const LenderAuthContext = createContext<LenderAuthContextValue | null>(null);

function writeDemoCookie(userId: string) {
  document.cookie = `${LENDER_SESSION_COOKIE}=${encodeURIComponent(userId)}; Path=/; Max-Age=${LENDER_SESSION_MAX_AGE_SECONDS}; SameSite=Lax`;
}

function toPublicDemoUser(user: (typeof DEMO_USERS)[number]): LenderUser {
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

function readDemoSession(): LenderUser | null {
  try {
    const raw = localStorage.getItem(LENDER_SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as LenderUser;
  } catch {
    localStorage.removeItem(LENDER_SESSION_STORAGE_KEY);
    return null;
  }
}

function persistDemoSession(user: LenderUser) {
  clearStaffSession(LENDER_STAFF_COOKIE_NAMES);
  localStorage.setItem(LENDER_SESSION_STORAGE_KEY, JSON.stringify(user));
  writeDemoCookie(user.id);
}

export function LenderAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<LenderUser | null>(null);
  const [authMode, setAuthMode] = useState<'platform' | 'demo' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  const logout = useCallback(() => {
    clearStaffSession(LENDER_STAFF_COOKIE_NAMES);
    setUser(null);
    setAuthMode(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
    try {
      const tokens = await apiLogin({ email: email.trim(), password });
      persistStaffSession(LENDER_STAFF_COOKIE_NAMES, tokens.access_token, tokens.refresh_token);
      const me = await getCurrentUser();
      const mapped = mapStaffUserToLender(me);
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

      if (isDemoAuthEnabled('lender')) {
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
            ? 'Could not reach the API. Use a demo lender account or start the platform API.'
            : platformMessage || 'Invalid email or password.',
      };
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const { access, refresh } = readStoredStaffTokens(LENDER_STAFF_COOKIE_NAMES);

      if (access) {
        setAccessToken(access);
        try {
          const me = await getCurrentUser();
          setUser(mapStaffUserToLender(me));
          setAuthMode('platform');
          setIsLoading(false);
          return;
        } catch {
          if (refresh) {
            try {
              const tokens = await apiRefresh(refresh);
              persistStaffSession(
                LENDER_STAFF_COOKIE_NAMES,
                tokens.access_token,
                tokens.refresh_token,
              );
              const me = await getCurrentUser();
              setUser(mapStaffUserToLender(me));
              setAuthMode('platform');
              setIsLoading(false);
              return;
            } catch {
              clearStaffSession(LENDER_STAFF_COOKIE_NAMES);
            }
          } else {
            clearStaffSession(LENDER_STAFF_COOKIE_NAMES);
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
      can: (permission: LenderPermission) =>
        user ? roleHasPermission(user.role, permission) : false,
    }),
    [user, isLoading, authMode, login, logout],
  );

  return <LenderAuthContext.Provider value={value}>{children}</LenderAuthContext.Provider>;
}

export function useLenderAuth() {
  const ctx = useContext(LenderAuthContext);
  if (!ctx) throw new Error('useLenderAuth must be used within LenderAuthProvider');
  return ctx;
}
