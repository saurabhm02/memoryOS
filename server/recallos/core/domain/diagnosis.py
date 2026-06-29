"""Root-cause diagnosis — a pure, deterministic walk over the prerequisite graph.

This is the platform's signature insight: given a set of weak concepts, find the
single upstream concept that is a prerequisite of the most of them. No LLM, no I/O,
no Cognee — just the graph and a set. Trivially unit-testable, and the same answer
every time.
"""

from __future__ import annotations

from dataclasses import dataclass

from .competency import PrereqGraph


@dataclass(frozen=True, slots=True)
class RootCause:
    """The diagnosed upstream concept and the weak concepts it explains."""

    concept: str
    resolves: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Diagnosis:
    """The result of a recall: the current weak set, the diagnosed root cause (if
    any), and an optional human-readable narration (flavor, never load-bearing)."""

    weak: frozenset[str]
    root_cause: RootCause | None
    narration: str | None = None


class RootCauseAnalyzer:
    """Stateless."""

    @staticmethod
    def analyze(graph: PrereqGraph, weak: set[str]) -> RootCause | None:
        """Return the concept that is a prerequisite of the most weak concepts, or
        None if no concept is upstream of any weak concept. Ties break
        deterministically by concept name (alphabetical) so the result is stable."""
        best: RootCause | None = None
        best_count = 0
        for concept in sorted(graph.concepts):
            covered = graph.targets(concept) & weak
            if len(covered) > best_count:
                best_count = len(covered)
                best = RootCause(concept=concept, resolves=tuple(sorted(covered)))
        return best
