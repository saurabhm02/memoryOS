"""RESET — wipe a learner's memory while preserving the account.

Clears both halves of a learner's state for one scope: the knowledge-graph dataset
(``MemoryEngine.reset``) and the durable evidence ledger. Per-scope only — never global.
This is the seam a scheduled demo-reset job (cron/endpoint) calls; today the admin script
``recallos.scripts.reset_demo`` invokes it with the production adapters.
"""

from __future__ import annotations

from recallos.core.application.ports import EvidenceLedger, MemoryEngine
from recallos.core.domain.identity import UserScope


class ResetLearnerMemory:
    def __init__(self, memory: MemoryEngine, ledger: EvidenceLedger) -> None:
        self._memory = memory
        self._ledger = ledger

    async def execute(self, scope: UserScope) -> None:
        await self._memory.reset(scope)
        await self._ledger.delete_scope(scope)
