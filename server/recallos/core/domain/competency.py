from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .errors import OntologyValidationError, UnknownConceptError


@dataclass(frozen=True, slots=True)
class Concept:
    """A single named competency. Edges live in the `PrereqGraph`, not here, so a
    concept stays a trivial, hashable value object."""

    name: str


@dataclass(frozen=True, slots=True)
class PrereqGraph:
    """A validated DAG of `prereq_of` edges over a closed set of concepts.

    Construct via `from_mapping`, which validates that every edge target is a known
    concept (no dangling edges) and that the graph is acyclic. Direct construction
    is possible but skips validation — prefer the factory.
    """

    # concept -> the concepts it is a prerequisite OF (its downstream dependents)
    _edges: Mapping[str, frozenset[str]]

    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Iterable[str]]) -> "PrereqGraph":
        edges = {src: frozenset(targets) for src, targets in mapping.items()}
        graph = cls(_edges=edges)
        graph._validate()
        return graph

    @property
    def concepts(self) -> frozenset[str]:
        return frozenset(self._edges)

    def targets(self, concept: str) -> frozenset[str]:
        """Concepts that `concept` is a prerequisite OF (its dependents)."""
        return self._edges.get(concept, frozenset())

    def prerequisites(self, concept: str) -> frozenset[str]:
        """Concepts that are prerequisites OF `concept` (its upstream)."""
        return frozenset(src for src, ts in self._edges.items() if concept in ts)

    def _validate(self) -> None:
        for src, targets in self._edges.items():
            missing = targets - self._edges.keys()
            if missing:
                raise OntologyValidationError(
                    f"concept {src!r} is a prerequisite of unknown "
                    f"concept(s): {sorted(missing)}"
                )

        visiting: set[str] = set()
        visited: set[str] = set()

        def walk(node: str, path: tuple[str, ...]) -> None:
            visiting.add(node)
            for nxt in self._edges[node]:
                if nxt in visiting:
                    cycle = (
                        path[path.index(nxt) :] + (nxt,) if nxt in path else (node, nxt)
                    )
                    raise OntologyValidationError(
                        "prerequisite cycle detected: " + " -> ".join(cycle)
                    )
                if nxt not in visited:
                    walk(nxt, path + (nxt,))
            visiting.discard(node)
            visited.add(node)

        for concept in self._edges:
            if concept not in visited:
                walk(concept, (concept,))


@dataclass(frozen=True, slots=True)
class Ontology:
    """A versioned, named competency graph for one learning domain. The vocabulary
    is closed: every concept the platform reasons about for this domain is a node in
    the graph, which is what eliminates free-text concept drift."""

    domain: str
    version: str
    title: str
    weak_threshold: float
    graph: PrereqGraph

    @property
    def vocabulary(self) -> frozenset[str]:
        return self.graph.concepts

    def require_known(self, concept: str) -> None:
        """Guard: raise if `concept` is not in this ontology's vocabulary."""
        if concept not in self.vocabulary:
            raise UnknownConceptError(
                f"{concept!r} is not in the {self.domain} v{self.version} vocabulary"
            )
