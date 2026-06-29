import { Loader2 } from "lucide-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/lib/auth/AuthProvider";

/** Landing spot for OAuth redirects and email-confirmation links. The Supabase client
 * parses the URL and emits an auth event; we just wait for the resolved status and route
 * onward. */
export function AuthCallbackScreen() {
  const { status } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (status === "authenticated") navigate("/", { replace: true });
    else if (status === "unauthenticated") navigate("/login", { replace: true });
  }, [status, navigate]);

  return (
    <div className="grid min-h-dvh place-items-center bg-bg">
      <div className="flex items-center gap-2 text-ink-muted">
        <Loader2 className="h-5 w-5 animate-spin" aria-hidden />
        <span className="text-sm">Completing sign-in…</span>
      </div>
    </div>
  );
}
