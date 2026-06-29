"""REMEMBER — record what an answer revealed."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from recallos.core.application.ports import (
    EvidenceLedger,
    MemoryEngine,
    OntologyRepository,
)
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation


@dataclass(frozen=True, slots=True)
class RememberResult:
    observation: Observation
    memory_written: bool


class RememberObservation:
    """Validates the concept against the domain's closed vocabulary, appends the
    observation to the durable ledger (the source of truth), then ingests it into the
    memory engine's knowledge graph. The ledger write is authoritative: if the memory
    ingest fails the observation is retained and recoverable, so the verb never
    silently loses data.
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

    async def execute(
        self,
        scope: UserScope,
        concept: str,
        score: int,
        at: datetime | None = None,
    ) -> RememberResult:
        ontology = self._ontologies.get(scope.domain)
        ontology.require_known(concept)

        observation = Observation(
            concept=concept, score=score, at=at or datetime.now(timezone.utc)
        )
        await self._ledger.append(scope, observation)

        try:
            await self._memory.ingest_evidence(scope, observation)
            memory_written = True
        except (
            Exception
        ):  # noqa: BLE001 — ledger is source of truth; memory is recoverable
            memory_written = False

        return RememberResult(observation=observation, memory_written=memory_written)
