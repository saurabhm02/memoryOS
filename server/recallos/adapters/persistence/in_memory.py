"""In-memory EvidenceLedger — the simplest production-ready implementation.

Real and complete for development, tests, and single-process runs without a
database. A Postgres-backed adapter replaces it behind the same port; the use-cases
never change.
"""

from __future__ import annotations

from collections import defaultdict

from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation


class InMemoryEvidenceLedger:
    def __init__(self) -> None:
        self._observations: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        self._mastered: dict[tuple[str, str], set[str]] = defaultdict(set)

    @staticmethod
    def _key(scope: UserScope) -> tuple[str, str]:
        return (scope.user_id, scope.domain)

    async def append(self, scope: UserScope, observation: Observation) -> None:
        self._observations[self._key(scope)].append(observation)

    async def observations(self, scope: UserScope) -> list[Observation]:
        return list(self._observations[self._key(scope)])

    async def mark_mastered(self, scope: UserScope, concept: str) -> None:
        self._mastered[self._key(scope)].add(concept)

    async def mastered(self, scope: UserScope) -> set[str]:
        return set(self._mastered[self._key(scope)])

    async def delete_scope(self, scope: UserScope) -> None:
        self._observations.pop(self._key(scope), None)
        self._mastered.pop(self._key(scope), None)
