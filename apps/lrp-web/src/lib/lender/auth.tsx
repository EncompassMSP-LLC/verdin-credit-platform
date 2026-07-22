'use client';

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useSyncExternalStore,
  type ReactNode,
} from 'react';
import { DEMO_USERS } from '@/lib/lender/data';
import {
  LENDER_SESSION_COOKIE,
  LENDER_SESSION_MAX_AGE_SECONDS,
  LENDER_SESSION_STORAGE_KEY,
} from '@/lib/lender/config';
import { roleHasPermission } from '@/lib/lender/permissions';
import type { LenderPermission, LenderUser } from '@/lib/lender/types';

type LenderAuthContextValue = {
  user: LenderUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ ok: true } | { ok: false; error: string }>;
  logout: () => void;
  can: (permission: LenderPermission) => boolean;
};

const LenderAuthContext = createContext<LenderAuthContextValue | null>(null);

function writeCookie(value: string) {
  document.cookie = `${LENDER_SESSION_COOKIE}=${encodeURIComponent(value)}; Path=/; Max-Age=${LENDER_SESSION_MAX_AGE_SECONDS}; SameSite=Lax`;
}

function clearCookie() {
  document.cookie = `${LENDER_SESSION_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax`;
}

function toPublicUser(user: (typeof DEMO_USERS)[number]): LenderUser {
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

function readSession(): LenderUser | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(LENDER_SESSION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as LenderUser;
  } catch {
    window.localStorage.removeItem(LENDER_SESSION_STORAGE_KEY);
    return null;
  }
}

let sessionSnapshot: LenderUser | null = null;
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

export function LenderAuthProvider({ children }: { children: ReactNode }) {
  const user = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);

  const login = useCallback(async (email: string, password: string) => {
    const match = DEMO_USERS.find(
      (u) => u.email.toLowerCase() === email.trim().toLowerCase() && u.password === password,
    );
    if (!match) {
      return { ok: false as const, error: 'Invalid email or password.' };
    }
    const publicUser = toPublicUser(match);
    window.localStorage.setItem(LENDER_SESSION_STORAGE_KEY, JSON.stringify(publicUser));
    writeCookie(publicUser.id);
    emit();
    return { ok: true as const };
  }, []);

  const logout = useCallback(() => {
    window.localStorage.removeItem(LENDER_SESSION_STORAGE_KEY);
    clearCookie();
    emit();
  }, []);

  const can = useCallback(
    (permission: LenderPermission) => {
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

  return <LenderAuthContext.Provider value={value}>{children}</LenderAuthContext.Provider>;
}

export function useLenderAuth() {
  const ctx = useContext(LenderAuthContext);
  if (!ctx) {
    throw new Error('useLenderAuth must be used within LenderAuthProvider');
  }
  return ctx;
}
