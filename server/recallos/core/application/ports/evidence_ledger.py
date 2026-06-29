"""Port: the durable, append-only record of scored observations and explicit mastery
overrides. It is the source of truth for mastery; it never stores concept
relationships (those belong to the authored ontology and the memory graph).
"""

from __future__ import annotations

from typing import Protocol

from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation


class EvidenceLedger(Protocol):
    async def append(self, scope: UserScope, observation: Observation) -> None:
        """Record one scored observation."""
        ...

    async def observations(self, scope: UserScope) -> list[Observation]:
        """All observations for this scope, for projecting mastery."""
        ...

    async def mark_mastered(self, scope: UserScope, concept: str) -> None:
        """Record that the learner has mastered a concept (the Forget verb): it is
        excluded from future planning regardless of historical evidence."""
        ...

    async def mastered(self, scope: UserScope) -> set[str]:
        """Concepts the learner has explicitly mastered/forgotten."""
        ...

    async def delete_scope(self, scope: UserScope) -> None:
        """Purge all ledger data for a scope (account/data reset). Per-scope — never
        global. Pairs with ``MemoryEngine.reset`` to wipe a learner's state."""
        ...
