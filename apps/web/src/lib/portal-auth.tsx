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
  getPortalMe,
  portalLogin as apiPortalLogin,
  portalRefresh as apiPortalRefresh,
  setAccessToken,
  type PortalMeResponse,
} from '@verdin/api-client';

interface PortalAuthContextValue {
  user: PortalMeResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const PortalAuthContext = createContext<PortalAuthContextValue | null>(null);

const PORTAL_ACCESS_TOKEN_KEY = 'verdin_portal_access_token';
const PORTAL_REFRESH_TOKEN_KEY = 'verdin_portal_refresh_token';

export function PortalAuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<PortalMeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(PORTAL_ACCESS_TOKEN_KEY);
    localStorage.removeItem(PORTAL_REFRESH_TOKEN_KEY);
    setAccessToken(null);
    setUser(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiPortalLogin({ email, password });
    localStorage.setItem(PORTAL_ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(PORTAL_REFRESH_TOKEN_KEY, tokens.refresh_token);
    setAccessToken(tokens.access_token);
    const me = await getPortalMe();
    setUser(me);
  }, []);

  useEffect(() => {
    const init = async () => {
      const storedAccessToken = localStorage.getItem(PORTAL_ACCESS_TOKEN_KEY);
      const storedRefreshToken = localStorage.getItem(PORTAL_REFRESH_TOKEN_KEY);

      if (!storedAccessToken) {
        setIsLoading(false);
        return;
      }

      setAccessToken(storedAccessToken);
      try {
        const me = await getPortalMe();
        setUser(me);
      } catch {
        if (storedRefreshToken) {
          try {
            const tokens = await apiPortalRefresh(storedRefreshToken);
            localStorage.setItem(PORTAL_ACCESS_TOKEN_KEY, tokens.access_token);
            localStorage.setItem(PORTAL_REFRESH_TOKEN_KEY, tokens.refresh_token);
            setAccessToken(tokens.access_token);
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
    }),
    [user, isLoading, login, logout],
  );

  return <PortalAuthContext.Provider value={value}>{children}</PortalAuthContext.Provider>;
}

export function usePortalAuth(): PortalAuthContextValue {
  const context = useContext(PortalAuthContext);
  if (!context) {
    throw new Error('usePortalAuth must be used within PortalAuthProvider');
  }
  return context;
}
