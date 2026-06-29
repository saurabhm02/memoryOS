"""Reusable adapter contract suites.

A contract suite encodes the behaviour the application layer relies on, independent of
any concrete adapter. Every implementation of a port must pass the *same* suite: the
in-memory doubles today, and `CogneeMemoryEngine` / `PostgresEvidenceLedger` once wired.
Subclass the contract, implement the factory, and the inherited tests run against your
adapter.

The MemoryEngine assertions are behavioural (operations succeed, return the right
types) rather than asserting graph internals — the deterministic graph logic lives in
the pure domain (and is covered there), and the root-cause decision reads the canonical
ontology, not the engine. The full product flow is exercised by the end-to-end
verification, not the contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from recallos.adapters.ontology import FileOntologyRepository
from recallos.core.application.ports import EvidenceLedger, MemifyDelta, MemoryEngine
from recallos.core.domain.competency import Ontology
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation

_ONTOLOGY_DIR = (
    Path(__file__).resolve().parents[2]
    / "recallos"
    / "apps"
    / "interview_prep"
    / "ontologies"
)


def _backend_sde() -> Ontology:
    return FileOntologyRepository(_ONTOLOGY_DIR).get("backend_sde")


def _scope(user_id: str = "contract_user") -> UserScope:
    return UserScope(user_id=user_id, domain="backend_sde")


def _obs(concept: str, score: int) -> Observation:
    return Observation(concept=concept, score=score, at=datetime.now(timezone.utc))


class MemoryEngineContract:
    """Behavioural contract every MemoryEngine adapter must satisfy."""

    async def make_engine(self) -> MemoryEngine:
        raise NotImplementedError

    async def test_provision_and_seed_graph_succeed(self):
        engine = await self.make_engine()
        scope = _scope()
        await engine.reset(scope)
        await engine.provision(scope)
        await engine.seed_graph(scope, _backend_sde())  # must not raise

    async def test_ingest_evidence_succeeds(self):
        engine = await self.make_engine()
        scope = _scope()
        await engine.provision(scope)
        await engine.seed_graph(scope, _backend_sde())
        await engine.ingest_evidence(scope, _obs("Caching", 2))  # must not raise

    async def test_derive_patterns_returns_a_delta(self):
        engine = await self.make_engine()
        scope = _scope()
        await engine.provision(scope)
        await engine.seed_graph(scope, _backend_sde())
        await engine.ingest_evidence(scope, _obs("Caching", 2))

        delta = await engine.derive_patterns(scope)
        assert isinstance(delta, MemifyDelta)
        assert delta.nodes_after >= 0
        assert delta.edges_after >= 0

    async def test_narrate_returns_optional_string_and_never_raises(self):
        engine = await self.make_engine()
        scope = _scope()
        await engine.provision(scope)
        await engine.seed_graph(scope, _backend_sde())
        result = await engine.narrate(scope, "Why does weakness in Caching trace upward?")
        assert result is None or isinstance(result, str)

    async def test_reset_succeeds(self):
        engine = await self.make_engine()
        scope = _scope("reset_user")
        await engine.provision(scope)
        await engine.seed_graph(scope, _backend_sde())
        await engine.reset(scope)  # must not raise


class EvidenceLedgerContract:
    """Behavioural contract every EvidenceLedger adapter must satisfy."""

    async def make_ledger(self) -> EvidenceLedger:
        raise NotImplementedError

    async def test_append_then_observations_preserves_order(self):
        ledger = await self.make_ledger()
        scope = _scope()
        await ledger.append(scope, _obs("Caching", 2))
        await ledger.append(scope, _obs("Indexing", 5))
        observations = await ledger.observations(scope)
        assert [o.concept for o in observations] == ["Caching", "Indexing"]

    async def test_observations_are_isolated_per_scope(self):
        ledger = await self.make_ledger()
        a, b = _scope("ledger_a"), _scope("ledger_b")
        await ledger.append(a, _obs("Caching", 2))
        assert len(await ledger.observations(a)) == 1
        assert await ledger.observations(b) == []

    async def test_mark_mastered_is_reflected_and_isolated(self):
        ledger = await self.make_ledger()
        a, b = _scope("ledger_a"), _scope("ledger_b")
        await ledger.mark_mastered(a, "Sharding")
        assert await ledger.mastered(a) == {"Sharding"}
        assert await ledger.mastered(b) == set()

    async def test_empty_scope_returns_empty(self):
        ledger = await self.make_ledger()
        scope = _scope("ledger_empty")
        assert await ledger.observations(scope) == []
        assert await ledger.mastered(scope) == set()
