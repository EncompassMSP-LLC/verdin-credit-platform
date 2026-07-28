'use client';

import {
  ApiClientError,
  configureApiClient,
  getRealtorMe,
  login as apiLogin,
  refreshToken as apiRefresh,
  setAccessToken,
  type RealtorSession,
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
  REALTOR_SESSION_COOKIE,
  REALTOR_SESSION_MAX_AGE_SECONDS,
  REALTOR_SESSION_STORAGE_KEY,
  REALTOR_STAFF_COOKIE_NAMES,
} from '@/lib/realtor/config';
import { DEMO_REALTOR_USERS } from '@/lib/realtor/data';
import { mapApiPermissions, roleHasPermission } from '@/lib/realtor/permissions';
import type { RealtorPermission, RealtorUser } from '@/lib/realtor/types';
import { getApiBaseUrl } from '@/lib/platform/config';

type RealtorAuthContextValue = {
  user: RealtorUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  authMode: 'platform' | 'demo' | null;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => void;
  can: (permission: RealtorPermission) => boolean;
  applySessionTokens: (access: string, refresh: string, session: RealtorSession) => void;
};

const RealtorAuthContext = createContext<RealtorAuthContextValue | null>(null);

function writeDemoCookie(userId: string) {
  document.cookie = `${REALTOR_SESSION_COOKIE}=${encodeURIComponent(userId)}; Path=/; Max-Age=${REALTOR_SESSION_MAX_AGE_SECONDS}; SameSite=Lax`;
}

function toPublicDemoUser(user: (typeof DEMO_REALTOR_USERS)[number]): RealtorUser {
  return {
    id: user.id,
    email: user.email,
    displayName: user.displayName,
    organizationId: user.organizationId,
    organizationName: user.organizationName,
    partnershipId: user.partnershipId,
    partnershipDisplayName: user.partnershipDisplayName,
    permissions: user.permissions,
    title: user.title,
  };
}

function mapSession(session: RealtorSession): RealtorUser {
  return {
    id: session.user_id,
    email: session.email,
    displayName: session.display_name,
    organizationId: session.partner_organization_id,
    organizationName: session.partner_organization_name,
    partnershipId: session.partnership_id,
    partnershipDisplayName: session.partnership_display_name,
    permissions: mapApiPermissions(session.permissions),
    title: 'Realtor partner',
  };
}

function readDemoSession(): RealtorUser | null {
  try {
    const raw = localStorage.getItem(REALTOR_SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as RealtorUser;
  } catch {
    localStorage.removeItem(REALTOR_SESSION_STORAGE_KEY);
    return null;
  }
}

function persistDemoSession(user: RealtorUser) {
  clearStaffSession(REALTOR_STAFF_COOKIE_NAMES);
  localStorage.setItem(REALTOR_SESSION_STORAGE_KEY, JSON.stringify(user));
  writeDemoCookie(user.id);
}

function clearDemoSession() {
  try {
    localStorage.removeItem(REALTOR_SESSION_STORAGE_KEY);
  } catch {
    /* ignore */
  }
  document.cookie = `${REALTOR_SESSION_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}

export function RealtorAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<RealtorUser | null>(null);
  const [authMode, setAuthMode] = useState<'platform' | 'demo' | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  const logout = useCallback(() => {
    clearStaffSession(REALTOR_STAFF_COOKIE_NAMES);
    clearDemoSession();
    setUser(null);
    setAuthMode(null);
  }, []);

  const applySessionTokens = useCallback(
    (access: string, refresh: string, session: RealtorSession) => {
      persistStaffSession(REALTOR_STAFF_COOKIE_NAMES, access, refresh);
      setUser(mapSession(session));
      setAuthMode('platform');
    },
    [],
  );

  const login = useCallback(async (email: string, password: string) => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
    try {
      const tokens = await apiLogin({ email: email.trim(), password });
      persistStaffSession(REALTOR_STAFF_COOKIE_NAMES, tokens.access_token, tokens.refresh_token);
      const me = await getRealtorMe();
      setUser(mapSession(me));
      setAuthMode('platform');
      return { ok: true as const };
    } catch (err) {
      clearStaffSession(REALTOR_STAFF_COOKIE_NAMES);
      const platformMessage =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : 'Platform sign-in failed.';

      if (isDemoAuthEnabled('realtor')) {
        const match = DEMO_REALTOR_USERS.find(
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

      const networkHint = isDemoAuthEnabled('realtor')
        ? 'Could not reach the API. Use a demo realtor account or start the platform API.'
        : 'Could not reach the API. Start the platform API and sign in with an invited realtor account.';

      return {
        ok: false as const,
        error:
          platformMessage.includes('fetch') || platformMessage.includes('Network')
            ? networkHint
            : platformMessage || 'Invalid email or password, or no realtor membership.',
      };
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const { access, refresh } = readStoredStaffTokens(REALTOR_STAFF_COOKIE_NAMES);

      if (access) {
        setAccessToken(access);
        try {
          const me = await getRealtorMe();
          setUser(mapSession(me));
          setAuthMode('platform');
          setIsLoading(false);
          return;
        } catch {
          if (refresh) {
            try {
              const tokens = await apiRefresh(refresh);
              persistStaffSession(
                REALTOR_STAFF_COOKIE_NAMES,
                tokens.access_token,
                tokens.refresh_token,
              );
              const me = await getRealtorMe();
              setUser(mapSession(me));
              setAuthMode('platform');
              setIsLoading(false);
              return;
            } catch {
              clearStaffSession(REALTOR_STAFF_COOKIE_NAMES);
            }
          } else {
            clearStaffSession(REALTOR_STAFF_COOKIE_NAMES);
          }
        }
      }

      if (isDemoAuthEnabled('realtor')) {
        const demo = readDemoSession();
        if (demo) {
          writeDemoCookie(demo.id);
          setUser(demo);
          setAuthMode('demo');
        }
      } else {
        clearDemoSession();
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
      applySessionTokens,
      can: (permission: RealtorPermission) =>
        user ? roleHasPermission(user.permissions, permission) : false,
    }),
    [user, isLoading, authMode, login, logout, applySessionTokens],
  );

  return <RealtorAuthContext.Provider value={value}>{children}</RealtorAuthContext.Provider>;
}

export function useRealtorAuth() {
  const ctx = useContext(RealtorAuthContext);
  if (!ctx) throw new Error('useRealtorAuth must be used within RealtorAuthProvider');
  return ctx;
}
