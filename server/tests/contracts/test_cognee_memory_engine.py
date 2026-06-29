"""Live contract test: CogneeMemoryEngine against real Cognee + Gemini.

Marked ``integration`` — excluded from the default fast suite (which stays Cognee-free
and offline). Run explicitly with::

    pytest -m integration

It needs the environment configured (GEMINI_API_KEY) and network for Kuzu's JSON
extension; in the sandboxed dev shell, run with the sandbox disabled.
"""

import pytest

from tests.contracts.base import MemoryEngineContract

# One shared event loop for the whole module: Cognee's Kuzu adapter holds loop-bound
# locks across calls, exactly as in a real single-loop process (FastAPI). A fresh loop
# per test (pytest-asyncio's default) would bind those locks to a stale loop.
pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="module")]


class TestCogneeMemoryEngine(MemoryEngineContract):
    async def make_engine(self):
        # Imported lazily so the default (offline) suite never imports cognee.
        from recallos.adapters.memory.cognee_engine import CogneeMemoryEngine
        from recallos.adapters.memory.cognee_runtime import init_cognee

        await init_cognee()  # idempotent
        return CogneeMemoryEngine()
