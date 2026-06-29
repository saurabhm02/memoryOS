/** Provider-agnostic auth types. Nothing outside `lib/auth` should know about Supabase;
 * the rest of the app speaks only in these shapes. */

export interface AuthUser {
  id: string;
  email: string | null;
  isDemo: boolean;
}

export interface AuthSession {
  accessToken: string;
  user: AuthUser;
}

export type OAuthProvider = "google" | "github";

export interface SignUpResult {
  /** True when the provider requires the user to confirm their email before signing in. */
  needsEmailConfirmation: boolean;
}

export class AuthServiceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthServiceError";
  }
}
