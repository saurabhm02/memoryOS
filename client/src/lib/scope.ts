import { useMemo } from "react";

import { useAuth } from "./auth/AuthProvider";
import type { Scope } from "./api/schemas";

export const DEFAULT_DOMAIN = "backend_sde";

/** Whether this learner has been provisioned, tracked per-user in the browser purely to
 * skip a redundant provision call. Provisioning is idempotent server-side, so this is an
 * optimization, not a source of truth. */
export function isStarted(userId: string): boolean {
  return (
    typeof window !== "undefined" &&
    window.localStorage.getItem(`recallos.started.${userId}`) === "1"
  );
}

export function markStarted(userId: string): void {
  window.localStorage.setItem(`recallos.started.${userId}`, "1");
}

/** The learner + domain for every request. The learner id is the authenticated user's
 * id (the same `sub` the backend derives from the verified token), so the browser can
 * never spoof whose memory it reads. */
export function useScope(): Scope {
  const { user } = useAuth();
  const userId = user?.id ?? "";
  return useMemo(() => ({ userId, domain: DEFAULT_DOMAIN }), [userId]);
}
