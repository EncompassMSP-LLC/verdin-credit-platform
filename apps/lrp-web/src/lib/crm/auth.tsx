'use client';

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from 'react';
import { DEMO_USERS } from '@/lib/crm/data';
import {
  CRM_SESSION_COOKIE,
  CRM_SESSION_MAX_AGE_SECONDS,
  CRM_SESSION_STORAGE_KEY,
} from '@/lib/crm/config';
import { roleHasPermission } from '@/lib/crm/permissions';
import type { CrmPermission, CrmUser } from '@/lib/crm/types';

type CrmAuthContextValue = {
  user: CrmUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => void;
  can: (permission: CrmPermission) => boolean;
};

const CrmAuthContext = createContext<CrmAuthContextValue | null>(null);

function writeCookie(value: string) {
  document.cookie = `${CRM_SESSION_COOKIE}=${encodeURIComponent(value)}; Path=/; Max-Age=${CRM_SESSION_MAX_AGE_SECONDS}; SameSite=Lax`;
}

function clearCookie() {
  document.cookie = `${CRM_SESSION_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function toPublicUser(user: (typeof DEMO_USERS)[number]): CrmUser {
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

function readSession(): CrmUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(CRM_SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as CrmUser;
  } catch {
    window.localStorage.removeItem(CRM_SESSION_STORAGE_KEY);
    return null;
  }
}

let sessionSnapshot: CrmUser | null = null;
const listeners = new Set<() => void>();

function emit() {
  sessionSnapshot = readSession();
  listeners.forEach((listener) => listener());
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot() {
  if (typeof window !== 'undefined' && sessionSnapshot === null) {
    sessionSnapshot = readSession();
    if (sessionSnapshot) {
      writeCookie(sessionSnapshot.id);
    }
  }
  return sessionSnapshot;
}

function getServerSnapshot() {
  return null;
}

export function CrmAuthProvider({ children }: { children: ReactNode }) {
  const user = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const login = useCallback(async (email: string, password: string) => {
    const match = DEMO_USERS.find(
      (u) => u.email.toLowerCase() === email.trim().toLowerCase() && u.password === password,
    );
    if (!match) {
      return { ok: false as const, error: 'Invalid email or password.' };
    }
    const publicUser = toPublicUser(match);
    window.localStorage.setItem(CRM_SESSION_STORAGE_KEY, JSON.stringify(publicUser));
    writeCookie(publicUser.id);
    emit();
    return { ok: true as const };
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(CRM_SESSION_STORAGE_KEY);
    clearCookie();
    emit();
  }, []);

  const can = useCallback(
    (permission: CrmPermission) => {
      if (!user) return false;
      return roleHasPermission(user.role, permission);
    },
    [user],
  );

  const value = useMemo(
    () => ({
      user,
      isLoading: false,
      isAuthenticated: Boolean(user),
      login,
      logout,
      can,
    }),
    [user, login, logout, can],
  );

  return <CrmAuthContext.Provider value={value}>{children}</CrmAuthContext.Provider>;
}

export function useCrmAuth() {
  const ctx = useContext(CrmAuthContext);
  if (!ctx) {
    throw new Error('useCrmAuth must be used within CrmAuthProvider');
  }
  return ctx;
}
