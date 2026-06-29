import type { CompetencyState } from "./api/schemas";

/** Mirrors the backend's mastery bands (recallos.core.domain.graph) so optimistic
 * updates classify a fresh score the same way the server will. The server reconciles
 * with recency-weighted truth on refetch. */
export const WEAK_THRESHOLD = 4;
const MASTERED_MARGIN = 0.6;

export function classifyState(score: number | null, mastered = false): CompetencyState {
  if (mastered) return "mastered";
  if (score === null) return "unvisited";
  if (score < WEAK_THRESHOLD) return "weak";
  if (score >= WEAK_THRESHOLD + MASTERED_MARGIN) return "mastered";
  return "medium";
}

interface StateMeta {
  label: string;
  /** CSS custom property holding the state color. */
  cssVar: string;
}

export const STATE_META: Record<CompetencyState, StateMeta> = {
  unvisited: { label: "Not yet practiced", cssVar: "--unvisited" },
  weak: { label: "Weak", cssVar: "--weak" },
  medium: { label: "Developing", cssVar: "--medium" },
  mastered: { label: "Mastered", cssVar: "--mastered" },
};
