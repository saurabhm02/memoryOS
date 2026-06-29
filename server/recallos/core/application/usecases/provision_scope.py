"""PROVISION — prepare a learner's memory and seed the authored knowledge graph."""

from __future__ import annotations

from recallos.core.application.ports import MemoryEngine, OntologyRepository
from recallos.core.domain.identity import UserScope


class ProvisionScope:
    """Prepares a learner's isolated memory space and seeds the authored prerequisite
    graph into the memory engine, so every subsequent verb reasons over one connected
    per-user knowledge graph. Run once when a learner starts a domain."""

    def __init__(self, memory: MemoryEngine, ontologies: OntologyRepository) -> None:
        self._memory = memory
        self._ontologies = ontologies

    async def execute(self, scope: UserScope) -> None:
        ontology = self._ontologies.get(scope.domain)
        await self._memory.provision(scope)
        await self._memory.seed_graph(scope, ontology)
