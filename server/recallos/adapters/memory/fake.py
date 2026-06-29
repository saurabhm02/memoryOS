"""A test double for the `MemoryEngine` port — fast, in-process, no Cognee.

This is NOT a production alternative to Cognee. The product runs on
`CogneeMemoryEngine`; this fake exists only to exercise the application layer
deterministically in unit tests. It records what it is told; it never fabricates
patterns or narration.
"""

from __future__ import annotations

from collections import defaultdict

from recallos.core.application.ports import MemifyDelta
from recallos.core.domain.competency import Ontology
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation


class FakeMemoryEngine:
    def __init__(self) -> None:
        self._evidence: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        self._seeded: set[tuple[str, str]] = set()

    @staticmethod
    def _key(scope: UserScope) -> tuple[str, str]:
        return (scope.user_id, scope.domain)

    async def provision(self, scope: UserScope) -> None:
        self._evidence.setdefault(self._key(scope), [])

    async def reset(self, scope: UserScope) -> None:
        self._evidence[self._key(scope)] = []
        self._seeded.discard(self._key(scope))

    async def seed_graph(self, scope: UserScope, ontology: Ontology) -> None:
        self._seeded.add(self._key(scope))

    async def ingest_evidence(self, scope: UserScope, observation: Observation) -> None:
        self._evidence[self._key(scope)].append(observation)

    async def derive_patterns(self, scope: UserScope) -> MemifyDelta:
        concept_count = len({o.concept for o in self._evidence[self._key(scope)]})
        return MemifyDelta(concept_count, concept_count, 0, 0, ())

    async def narrate(self, scope: UserScope, prompt: str) -> str | None:
        return None
