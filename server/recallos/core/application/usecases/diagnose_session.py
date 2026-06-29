"""RECALL — surface the single upstream concept to fix first."""

from __future__ import annotations

from recallos.core.application.ports import (
    EvidenceLedger,
    MemoryEngine,
    OntologyRepository,
)
from recallos.core.domain.diagnosis import Diagnosis, RootCause, RootCauseAnalyzer
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import MasteryProjector


class DiagnoseSession:
    """Projects mastery from the ledger, computes the weak set (minus concepts the
    learner has explicitly mastered), then finds the root cause by traversing the
    CANONICAL ontology graph with the deterministic `RootCauseAnalyzer` — independent
    of any memory-engine graph query. The memory engine narrates the diagnosis on top.
    """

    def __init__(
        self,
        ledger: EvidenceLedger,
        memory: MemoryEngine,
        ontologies: OntologyRepository,
    ) -> None:
        self._ledger = ledger
        self._memory = memory
        self._ontologies = ontologies

    async def execute(self, scope: UserScope) -> Diagnosis:
        ontology = self._ontologies.get(scope.domain)

        observations = await self._ledger.observations(scope)
        mastery = MasteryProjector.project(observations)
        mastered = await self._ledger.mastered(scope)
        weak = mastery.weak_set(ontology.weak_threshold) - mastered

        root = RootCauseAnalyzer.analyze(ontology.graph, weak)
        narration = await self._narrate(scope, weak, root)
        return Diagnosis(weak=frozenset(weak), root_cause=root, narration=narration)

    async def _narrate(
        self, scope: UserScope, weak: set[str], root: RootCause | None
    ) -> str | None:
        if root is None:
            return None
        prompt = (
            f"Explain why weakness in {', '.join(sorted(weak))} traces to the "
            f"prerequisite concept {root.concept}."
        )
        try:
            return await self._memory.narrate(scope, prompt)
        except Exception:  # noqa: BLE001 — narration is flavor, never load-bearing
            return None
