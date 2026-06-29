import type { Session, User } from "@supabase/supabase-js";

import { supabase } from "./supabaseClient";
import {
  AuthServiceError,
  type AuthSession,
  type AuthUser,
  type OAuthProvider,
  type SignUpResult,
} from "./types";

const DEMO_EMAIL = import.meta.env.VITE_DEMO_EMAIL ?? "";
const DEMO_PASSWORD = import.meta.env.VITE_DEMO_PASSWORD ?? "";

function callbackUrl(): string {
  return `${window.location.origin}/auth/callback`;
}

function toUser(user: User): AuthUser {
  return {
    id: user.id,
    email: user.email ?? null,
    isDemo: Boolean(DEMO_EMAIL) && user.email === DEMO_EMAIL,
  };
}

function toSession(session: Session | null): AuthSession | null {
  if (!session?.user) return null;
  return { accessToken: session.access_token, user: toUser(session.user) };
}

/** The auth boundary the app depends on. The Supabase implementation lives below; the
 * rest of the app only ever sees this interface and the `authService` singleton. */
export interface AuthService {
  getSession(): Promise<AuthSession | null>;
  getAccessToken(): Promise<string | null>;
  signInWithPassword(email: string, password: string): Promise<AuthSession>;
  signUp(email: string, password: string): Promise<SignUpResult>;
  signInWithDemo(): Promise<AuthSession>;
  signInWithOAuth(provider: OAuthProvider): Promise<void>;
  resetPassword(email: string): Promise<void>;
  signOut(): Promise<void>;
  onAuthStateChange(cb: (session: AuthSession | null) => void): () => void;
  hasDemo(): boolean;
}

class SupabaseAuthService implements AuthService {
  async getSession(): Promise<AuthSession | null> {
    const { data } = await supabase.auth.getSession();
    return toSession(data.session);
  }

  async getAccessToken(): Promise<string | null> {
    // getSession() returns the cached token and silently refreshes it when near expiry.
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  }

  async signInWithPassword(email: string, password: string): Promise<AuthSession> {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) throw new AuthServiceError(error.message);
    const session = toSession(data.session);
    if (!session) throw new AuthServiceError("Sign-in returned no session.");
    return session;
  }

  async signUp(email: string, password: string): Promise<SignUpResult> {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: { emailRedirectTo: callbackUrl() },
    });
    if (error) throw new AuthServiceError(error.message);
    // When confirmation is required, Supabase returns a user but no session.
    return { needsEmailConfirmation: !data.session };
  }

  async signInWithDemo(): Promise<AuthSession> {
    if (!this.hasDemo()) {
      throw new AuthServiceError("The demo account is not configured.");
    }
    return this.signInWithPassword(DEMO_EMAIL, DEMO_PASSWORD);
  }

  async signInWithOAuth(provider: OAuthProvider): Promise<void> {
    const { error } = await supabase.auth.signInWithOAuth({
      provider,
      options: { redirectTo: callbackUrl() },
    });
    if (error) throw new AuthServiceError(error.message);
  }

  async resetPassword(email: string): Promise<void> {
    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: callbackUrl(),
    });
    if (error) throw new AuthServiceError(error.message);
  }

  async signOut(): Promise<void> {
    const { error } = await supabase.auth.signOut();
    if (error) throw new AuthServiceError(error.message);
  }

  onAuthStateChange(cb: (session: AuthSession | null) => void): () => void {
    const { data } = supabase.auth.onAuthStateChange((_event, session) => {
      cb(toSession(session));
    });
    return () => data.subscription.unsubscribe();
  }

  hasDemo(): boolean {
    return Boolean(DEMO_EMAIL && DEMO_PASSWORD);
  }
}

export const authService: AuthService = new SupabaseAuthService();
