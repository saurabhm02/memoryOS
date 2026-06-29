"""IMPROVE — derive emergent patterns from accumulated evidence (memify)."""

from __future__ import annotations

from recallos.core.application.ports import MemifyDelta, MemoryEngine
from recallos.core.domain.identity import UserScope


class ImproveMemory:
    """Triggers pattern derivation (memify) in the memory engine and returns the
    before/after delta for display. Thin by design — the work lives in the engine —
    but it keeps the verb explicit and independently swappable."""

    def __init__(self, memory: MemoryEngine) -> None:
        self._memory = memory

    async def execute(self, scope: UserScope) -> MemifyDelta:
        return await self._memory.derive_patterns(scope)
