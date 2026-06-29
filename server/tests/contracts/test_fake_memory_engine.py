"""The fake memory engine must satisfy the MemoryEngine contract. CogneeMemoryEngine
will be held to the identical suite once the environment is provisioned.
"""

from recallos.adapters.memory import FakeMemoryEngine
from tests.contracts.base import MemoryEngineContract


class TestFakeMemoryEngine(MemoryEngineContract):
    async def make_engine(self) -> FakeMemoryEngine:
        return FakeMemoryEngine()
