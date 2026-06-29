"""Live contract test: PostgresEvidenceLedger against the real (Aiven) database.

Marked ``integration``. Needs DATABASE_URL configured. No Cognee/Gemini involved, so it
runs without disabling the sandbox. Each test starts from a clean slate for its scopes.
"""

import pytest

from recallos.config import settings
from recallos.core.domain.identity import UserScope
from tests.contracts.base import EvidenceLedgerContract

pytestmark = pytest.mark.integration

_TEST_USER_IDS = ["contract_user", "ledger_a", "ledger_b", "ledger_empty", "reset_user"]


class TestPostgresLedger(EvidenceLedgerContract):
    async def make_ledger(self):
        from recallos.adapters.persistence import PostgresEvidenceLedger

        ledger = PostgresEvidenceLedger(settings.database_url)
        ledger.create_all()
        for user_id in _TEST_USER_IDS:
            await ledger.delete_scope(UserScope(user_id=user_id, domain="backend_sde"))
        return ledger
