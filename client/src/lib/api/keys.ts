import type { Scope } from "./schemas";

/** Centralized React Query keys, scoped by learner + domain. */
export const queryKeys = {
  health: ["health"] as const,
  graph: (scope: Scope) => ["graph", scope.userId, scope.domain] as const,
  diagnosis: (scope: Scope) => ["diagnosis", scope.userId, scope.domain] as const,
};
