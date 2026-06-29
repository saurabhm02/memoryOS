"""Application-layer tests: provisioning + the four verbs, wired over the fake memory
engine and the real authored ontology. This is the Clean Architecture equivalent of
the headless gate — deterministic, no external services.

`FakeMemoryEngine` is a TEST DOUBLE; production runs on CogneeMemoryEngine.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from recallos.adapters.memory import FakeMemoryEngine
from recallos.adapters.ontology import FileOntologyRepository
from recallos.adapters.persistence import InMemoryEvidenceLedger
from recallos.core.application.usecases import (
    DiagnoseSession,
    ForgetConcept,
    ImproveMemory,
    ProvisionScope,
    RememberObservation,
)
from recallos.core.domain.errors import UnknownConceptError
from recallos.core.domain.identity import UserScope

_BACKEND = Path(__file__).resolve().parents[2]
_ONTOLOGY_DIR = _BACKEND / "recallos" / "apps" / "interview_prep" / "ontologies"
_BASE = datetime(2026, 1, 1)

# The convergent pattern: three concepts that depend on Consistency Models all land
# weak; Consistency Models itself gets no direct evidence, so it can only be reached
# by traversing prerequisites in the knowledge graph.
RIGGED = (
    [("Caching", 2)] * 4
    + [("Database Round Trips", 1)] * 5
    + [("Distributed Transactions", 3)] * 3
    + [("Indexing", 5)] * 2  # a strength — proves demonstrated != weak
    + [("Sharding", 2)] * 3
    + [("Load Balancing", 4)] * 3  # exactly at threshold — not weak (< is strict)
)


@pytest.fixture
def wiring():
    return (
        FileOntologyRepository(_ONTOLOGY_DIR),
        InMemoryEvidenceLedger(),
        FakeMemoryEngine(),
    )


@pytest.fixture
def scope():
    return UserScope(user_id="u1", domain="backend_sde")


async def _remember_rigged(remember: RememberObservation, scope: UserScope) -> None:
    for i, (concept, score) in enumerate(RIGGED):
        await remember.execute(scope, concept, score, at=_BASE + timedelta(minutes=i))


async def test_provision_remember_recall_finds_root_cause(wiring, scope):
    ontologies, ledger, memory = wiring
    await ProvisionScope(memory, ontologies).execute(scope)
    await _remember_rigged(RememberObservation(ledger, memory, ontologies), scope)

    diagnosis = await DiagnoseSession(ledger, memory, ontologies).execute(scope)
    assert diagnosis.root_cause is not None
    assert diagnosis.root_cause.concept == "Consistency Models"
    assert diagnosis.root_cause.resolves == (
        "Caching",
        "Database Round Trips",
        "Distributed Transactions",
    )


async def test_remember_writes_to_ledger_and_memory(wiring, scope):
    ontologies, ledger, memory = wiring
    result = await RememberObservation(ledger, memory, ontologies).execute(
        scope, "Caching", 2, at=_BASE
    )
    assert result.memory_written is True
    assert len(await ledger.observations(scope)) == 1


async def test_remember_rejects_unknown_concept(wiring, scope):
    ontologies, ledger, memory = wiring
    with pytest.raises(UnknownConceptError):
        await RememberObservation(ledger, memory, ontologies).execute(
            scope, "Kubernetes", 3, at=_BASE
        )


async def test_memory_failure_is_recoverable(wiring, scope):
    ontologies, ledger, _ = wiring

    class FailingMemory:
        async def provision(self, scope): ...
        async def reset(self, scope): ...
        async def seed_graph(self, scope, ontology): ...
        async def prereq_graph(self, scope): ...
        async def ingest_evidence(self, scope, observation):
            raise RuntimeError("cognify unavailable")

        async def derive_patterns(self, scope): ...
        async def narrate(self, scope, prompt):
            return None

    result = await RememberObservation(ledger, FailingMemory(), ontologies).execute(
        scope, "Caching", 2, at=_BASE
    )
    assert result.memory_written is False
    # The ledger still has it — the durable source of truth is intact.
    assert len(await ledger.observations(scope)) == 1


async def test_forget_removes_concept_from_weak_set_but_root_holds(wiring, scope):
    ontologies, ledger, memory = wiring
    await ProvisionScope(memory, ontologies).execute(scope)
    await _remember_rigged(RememberObservation(ledger, memory, ontologies), scope)
    diagnose = DiagnoseSession(ledger, memory, ontologies)

    before = await diagnose.execute(scope)
    assert "Sharding" in before.weak

    await ForgetConcept(ledger, ontologies).execute(scope, "Sharding")

    after = await diagnose.execute(scope)
    assert "Sharding" not in after.weak
    assert after.root_cause is not None
    assert after.root_cause.concept == "Consistency Models"


async def test_improve_returns_truthful_delta(wiring, scope):
    ontologies, ledger, memory = wiring
    await ProvisionScope(memory, ontologies).execute(scope)
    await _remember_rigged(RememberObservation(ledger, memory, ontologies), scope)

    delta = await ImproveMemory(memory).execute(scope)
    # Six distinct concepts were observed; the fake never fabricates patterns.
    assert delta.nodes_after == 6
    assert delta.derived_patterns == ()


async def test_empty_history_has_no_root_cause(wiring, scope):
    ontologies, ledger, memory = wiring
    await ProvisionScope(memory, ontologies).execute(scope)

    diagnosis = await DiagnoseSession(ledger, memory, ontologies).execute(scope)
    assert diagnosis.weak == frozenset()
    assert diagnosis.root_cause is None
