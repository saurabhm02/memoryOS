"""The in-memory ledger must satisfy the EvidenceLedger contract. PostgresEvidenceLedger
will be held to the identical suite once the environment is provisioned.
"""

from recallos.adapters.persistence import InMemoryEvidenceLedger
from tests.contracts.base import EvidenceLedgerContract


class TestInMemoryLedger(EvidenceLedgerContract):
    async def make_ledger(self) -> InMemoryEvidenceLedger:
        return InMemoryEvidenceLedger()
