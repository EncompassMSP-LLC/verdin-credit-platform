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
  getCurrentUser,
  login as apiLogin,
  refreshToken as apiRefreshToken,
  setAccessToken,
  type User,
} from '@verdin/api-client';

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const ACCESS_TOKEN_KEY = 'verdin_access_token';
const REFRESH_TOKEN_KEY = 'verdin_refresh_token';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    setAccessToken(null);
    setUser(null);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const tokens = await apiLogin({ email, password });
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    setAccessToken(tokens.access_token);
    const me = await getCurrentUser();
    setUser(me);
  }, []);

  useEffect(() => {
    const init = async () => {
      const storedAccessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
      const storedRefreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

      if (!storedAccessToken) {
        setIsLoading(false);
        return;
      }

      setAccessToken(storedAccessToken);
      try {
        const me = await getCurrentUser();
        setUser(me);
      } catch {
        if (storedRefreshToken) {
          try {
            const tokens = await apiRefreshToken(storedRefreshToken);
            localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access_token);
            localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
            setAccessToken(tokens.access_token);
            const me = await getCurrentUser();
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
    init();
  }, [logout]);

  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user,
      login,
      logout,
    }),
    [user, isLoading, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
