import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { authService } from "./AuthService";
import type { AuthUser, OAuthProvider, SignUpResult } from "./types";

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

interface AuthContextValue {
  status: AuthStatus;
  user: AuthUser | null;
  hasDemo: boolean;
  signIn(email: string, password: string): Promise<void>;
  signUp(email: string, password: string): Promise<SignUpResult>;
  signInWithDemo(): Promise<void>;
  signInWithOAuth(provider: OAuthProvider): Promise<void>;
  resetPassword(email: string): Promise<void>;
  signOut(): Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    let active = true;
    const apply = (nextUser: AuthUser | null) => {
      if (!active) return;
      setUser(nextUser);
      setStatus(nextUser ? "authenticated" : "unauthenticated");
    };

    void authService.getSession().then((session) => apply(session?.user ?? null));
    const unsubscribe = authService.onAuthStateChange((session) =>
      apply(session?.user ?? null),
    );

    return () => {
      active = false;
      unsubscribe();
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      hasDemo: authService.hasDemo(),
      signIn: async (email, password) => {
        await authService.signInWithPassword(email, password);
      },
      signUp: (email, password) => authService.signUp(email, password),
      signInWithDemo: async () => {
        await authService.signInWithDemo();
      },
      signInWithOAuth: (provider) => authService.signInWithOAuth(provider),
      resetPassword: (email) => authService.resetPassword(email),
      signOut: async () => {
        await authService.signOut();
      },
    }),
    [status, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider.");
  return ctx;
}
