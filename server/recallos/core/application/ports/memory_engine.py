"""Port: the memory engine — RecallOS's core technology and differentiator.

This is NOT a generic storage abstraction. It is the knowledge-graph + retrieval +
reasoning engine the product is built around (Cognee in production). It holds the
per-user knowledge graph — the authored prerequisite backbone is *seeded into* it and
grows with every observation — derives emergent patterns (memify), and narrates over
the graph.

The integration layer exists to isolate Cognee's implementation details and keep the
system testable — not to make Cognee optional. The in-memory `FakeMemoryEngine` is a
test double; the product runs on Cognee.

Determinism is preserved without sidelining the engine: prerequisite *edges* are
authored data (never LLM-inferred) and seeded here, while the engine serves the graph
for traversal, reasoning, and retrieval. The final root-cause *selection* is a tiny
pure function over the graph this engine returns.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from recallos.core.domain.competency import Ontology
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation


@dataclass(frozen=True, slots=True)
class MemifyDelta:
    """Before/after sizes of the knowledge graph plus any newly derived pattern
    labels, for display after an Improve."""

    nodes_before: int
    nodes_after: int
    edges_before: int
    edges_after: int
    derived_patterns: tuple[str, ...] = ()


class MemoryEngine(Protocol):
    async def provision(self, scope: UserScope) -> None:
        """Prepare an isolated per-user memory space. Per-user — never global."""
        ...

    async def reset(self, scope: UserScope) -> None:
        """Clear this scope's memory only. Never affects other users."""
        ...

    async def seed_graph(self, scope: UserScope, ontology: Ontology) -> None:
        """Author the prerequisite graph into the knowledge graph. Edges are authored
        data (never LLM-inferred), so the structural backbone is deterministic while
        living inside the engine alongside evidence and derived patterns."""
        ...

    async def ingest_evidence(self, scope: UserScope, observation: Observation) -> None:
        """Add an observation to the knowledge graph and run cognify so it becomes
        connected, queryable memory."""
        ...

    async def derive_patterns(self, scope: UserScope) -> MemifyDelta:
        """Run memify to derive emergent patterns over accumulated evidence."""
        ...

    async def narrate(self, scope: UserScope, prompt: str) -> str | None:
        """Graph-grounded natural-language narration. Returns None if unavailable;
        callers treat it as flavor and never depend on it for a decision."""
        ...
