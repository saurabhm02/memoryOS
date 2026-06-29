import { Loader2 } from "lucide-react";
import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { useAuth } from "@/lib/auth/AuthProvider";

function FullScreenLoader() {
  return (
    <div className="grid min-h-dvh place-items-center bg-bg">
      <Loader2 className="h-6 w-6 animate-spin text-ink-subtle" aria-label="Loading" />
    </div>
  );
}

/** Gates the authenticated app. While the session resolves we hold on a loader (no
 * flicker), then either render or bounce to the landing page. */
export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  if (status === "loading") return <FullScreenLoader />;
  if (status === "unauthenticated") return <Navigate to="/landing" replace />;
  return <>{children}</>;
}

/** Public auth pages — already-authenticated users skip straight to the app. */
export function PublicOnlyRoute({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  if (status === "loading") return <FullScreenLoader />;
  if (status === "authenticated") return <Navigate to="/" replace />;
  return <>{children}</>;
}
