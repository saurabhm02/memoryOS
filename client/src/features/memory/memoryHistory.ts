import type { CompetencyGraph, CompetencyState } from "@/lib/api/schemas";

/** A point-in-time summary of the learner's competency graph. Tracked client-side so
 * the Memory timeline shows real progression without requiring server-side history. */
export interface MemorySnapshot {
  at: number;
  unvisited: number;
  weak: number;
  medium: number;
  mastered: number;
  rootCause: string | null;
}

const MAX = 12;
const key = (userId: string) => `recallos.history.${userId}`;

export function snapshotOf(graph: CompetencyGraph): MemorySnapshot {
  const counts: Record<CompetencyState, number> = {
    unvisited: 0,
    weak: 0,
    medium: 0,
    mastered: 0,
  };
  for (const node of graph.nodes) counts[node.state] += 1;
  return { at: Date.now(), ...counts, rootCause: graph.root_cause?.concept ?? null };
}

export function getHistory(userId: string): MemorySnapshot[] {
  try {
    return JSON.parse(localStorage.getItem(key(userId)) ?? "[]") as MemorySnapshot[];
  } catch {
    return [];
  }
}

function sameShape(a: MemorySnapshot, b: MemorySnapshot): boolean {
  return (
    a.unvisited === b.unvisited &&
    a.weak === b.weak &&
    a.medium === b.medium &&
    a.mastered === b.mastered &&
    a.rootCause === b.rootCause
  );
}

/** Append a snapshot, skipping consecutive duplicates. Returns the new history. */
export function recordSnapshot(
  userId: string,
  snapshot: MemorySnapshot,
): MemorySnapshot[] {
  const history = getHistory(userId);
  const last = history[history.length - 1];
  if (last && sameShape(last, snapshot)) return history;
  const next = [...history, snapshot].slice(-MAX);
  localStorage.setItem(key(userId), JSON.stringify(next));
  return next;
}
