import { beforeEach, describe, expect, it } from "vitest";

import type { CompetencyGraph } from "@/lib/api/schemas";

import { getHistory, recordSnapshot, snapshotOf } from "./memoryHistory";

function graph(overrides: Partial<CompetencyGraph> = {}): CompetencyGraph {
  return {
    nodes: [
      { concept: "Caching", state: "weak", score: 2 },
      { concept: "Indexing", state: "mastered", score: 4.8 },
      { concept: "Sharding", state: "unvisited", score: null },
    ],
    edges: [],
    root_cause: null,
    ...overrides,
  };
}

describe("memoryHistory", () => {
  beforeEach(() => localStorage.clear());

  it("counts states and captures the root cause", () => {
    const snapshot = snapshotOf(
      graph({ root_cause: { concept: "Consistency Models", resolves: ["Caching"] } }),
    );
    expect(snapshot.weak).toBe(1);
    expect(snapshot.mastered).toBe(1);
    expect(snapshot.unvisited).toBe(1);
    expect(snapshot.rootCause).toBe("Consistency Models");
  });

  it("dedupes consecutive identical snapshots", () => {
    recordSnapshot("u", snapshotOf(graph()));
    const history = recordSnapshot("u", snapshotOf(graph()));
    expect(history).toHaveLength(1);
  });

  it("appends when the shape changes", () => {
    recordSnapshot("u", snapshotOf(graph()));
    const changed = graph({
      nodes: [{ concept: "Caching", state: "mastered", score: 5 }],
    });
    const history = recordSnapshot("u", snapshotOf(changed));
    expect(history).toHaveLength(2);
    expect(getHistory("u")).toHaveLength(2);
  });
});
