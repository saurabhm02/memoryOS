"""End-to-end: Remember -> Recall -> Improve -> Forget with REAL Cognee + PostgreSQL.

The full product flow over the real adapters — PostgresEvidenceLedger (Aiven),
CogneeMemoryEngine (Cognee 1.2.1 + Gemini), FileOntologyRepository — driven through the
application use-cases.

Marked ``integration`` and pinned to one module event loop (Cognee's Kuzu locks are
loop-bound). Needs the env (GEMINI_API_KEY), the Aiven DB, and network for Kuzu's
extension — run with the sandbox disabled.
"""

from datetime import datetime, timezone

import pytest

from recallos.adapters.ontology import FileOntologyRepository
from recallos.apps.interview_prep import ONTOLOGY_DIR
from recallos.config import settings
from recallos.core.application.ports import MemifyDelta
from recallos.core.application.usecases import (
    DiagnoseSession,
    ForgetConcept,
    ImproveMemory,
    ProvisionScope,
    RememberObservation,
)
from recallos.core.domain.identity import UserScope

pytestmark = [pytest.mark.integration, pytest.mark.asyncio(loop_scope="module")]

# Minimal convergent set (keeps live cognify calls low): three concepts that depend on
# Consistency Models land weak, plus Sharding (for the forget step) and one strength.
_RIGGED = [
    ("Caching", 2),
    ("Database Round Trips", 1),
    ("Distributed Transactions", 3),
    ("Indexing", 5),
    ("Sharding", 2),
]


async def test_full_flow_remember_recall_improve_forget():
    from recallos.adapters.memory.cognee_engine import CogneeMemoryEngine
    from recallos.adapters.memory.cognee_runtime import init_cognee
    from recallos.adapters.persistence import PostgresEvidenceLedger

    await init_cognee()
    ontologies = FileOntologyRepository(ONTOLOGY_DIR)
    ledger = PostgresEvidenceLedger(settings.database_url)
    ledger.create_all()
    memory = CogneeMemoryEngine()
    scope = UserScope(user_id="e2e_user", domain="backend_sde")

    # Clean slate in both stores.
    await ledger.delete_scope(scope)
    await memory.reset(scope)

    # PROVISION — seed the authored ontology into Cognee.
    await ProvisionScope(memory, ontologies).execute(scope)

    # REMEMBER — each observation lands in the ledger and the Cognee graph.
    remember = RememberObservation(ledger, memory, ontologies)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i, (concept, score) in enumerate(_RIGGED):
        result = await remember.execute(scope, concept, score, at=base.replace(minute=i))
        assert result.memory_written is True

    # RECALL — deterministic root cause from the canonical ontology + Cognee narration.
    diagnosis = await DiagnoseSession(ledger, memory, ontologies).execute(scope)
    assert diagnosis.root_cause is not None
    assert diagnosis.root_cause.concept == "Consistency Models"
    assert "Caching" in diagnosis.root_cause.resolves
    assert diagnosis.narration is None or isinstance(diagnosis.narration, str)
    assert "Sharding" in diagnosis.weak

    # IMPROVE — memify enrichment over the accumulated graph.
    delta = await ImproveMemory(memory).execute(scope)
    assert isinstance(delta, MemifyDelta)

    # FORGET — a mastered concept leaves the weak set; the root cause still holds.
    await ForgetConcept(ledger, ontologies).execute(scope, "Sharding")
    after = await DiagnoseSession(ledger, memory, ontologies).execute(scope)
    assert "Sharding" not in after.weak
    assert after.root_cause is not None
    assert after.root_cause.concept == "Consistency Models"
