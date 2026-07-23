'use client';

import {
  configureApiClient,
  getPortalMe,
  portalLogin as apiPortalLogin,
  portalRefresh as apiPortalRefresh,
  setAccessToken,
  type PortalMeResponse,
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
import {
  getApiBaseUrl,
  PLATFORM_ACCESS_STORAGE,
  PLATFORM_REFRESH_STORAGE,
} from '@/lib/platform/config';
import { clearAuthCookies, setAuthCookies } from '@/lib/platform/cookies';

interface PlatformAuthContextValue {
  user: PortalMeResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  apiConfigured: boolean;
}

const PlatformAuthContext = createContext<PlatformAuthContextValue | null>(null);

function persistSession(accessToken: string, refreshToken: string) {
  localStorage.setItem(PLATFORM_ACCESS_STORAGE, accessToken);
  localStorage.setItem(PLATFORM_REFRESH_STORAGE, refreshToken);
  setAuthCookies(accessToken, refreshToken);
  setAccessToken(accessToken);
}

function clearSession() {
  localStorage.removeItem(PLATFORM_ACCESS_STORAGE);
  localStorage.removeItem(PLATFORM_REFRESH_STORAGE);
  clearAuthCookies();
  setAccessToken(null);
}

export function PlatformAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<PortalMeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
  }, []);

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    configureApiClient({ baseUrl: getApiBaseUrl() });
    const tokens = await apiPortalLogin({ email, password });
    persistSession(tokens.access_token, tokens.refresh_token);
    const me = await getPortalMe();
    setUser(me);
  }, []);

  useEffect(() => {
    const init = async () => {
      configureApiClient({ baseUrl: getApiBaseUrl() });
      const storedAccess = localStorage.getItem(PLATFORM_ACCESS_STORAGE);
      const storedRefresh = localStorage.getItem(PLATFORM_REFRESH_STORAGE);

      if (!storedAccess) {
        setIsLoading(false);
        return;
      }

      setAccessToken(storedAccess);
      try {
        const me = await getPortalMe();
        setUser(me);
        if (storedRefresh) {
          setAuthCookies(storedAccess, storedRefresh);
        }
      } catch {
        if (storedRefresh) {
          try {
            const tokens = await apiPortalRefresh(storedRefresh);
            persistSession(tokens.access_token, tokens.refresh_token);
            const me = await getPortalMe();
            setUser(me);
          } catch {
            logout();
          }
        } else {
          logout();
        }
      } finally {
        setIsLoading(false);
      }
    };

    void init();
  }, [logout]);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: user !== null,
      login,
      logout,
      apiConfigured: Boolean(getApiBaseUrl()),
    }),
    [user, isLoading, login, logout],
  );

  return <PlatformAuthContext.Provider value={value}>{children}</PlatformAuthContext.Provider>;
}

export function usePlatformAuth(): PlatformAuthContextValue {
  const context = useContext(PlatformAuthContext);
  if (!context) {
    throw new Error('usePlatformAuth must be used within PlatformAuthProvider');
  }
  return context;
}
