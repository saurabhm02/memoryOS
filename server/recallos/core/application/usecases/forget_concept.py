"""FORGET — stop drilling a concept the learner has mastered."""

from __future__ import annotations

from recallos.core.application.ports import EvidenceLedger, OntologyRepository
from recallos.core.domain.identity import UserScope


class ForgetConcept:
    """Records that the learner has mastered a concept so planning excludes it,
    regardless of historical evidence. The evidence itself is retained — forget means
    "stop spending attention here," not "erase history"."""

    def __init__(self, ledger: EvidenceLedger, ontologies: OntologyRepository) -> None:
        self._ledger = ledger
        self._ontologies = ontologies

    async def execute(self, scope: UserScope, concept: str) -> None:
        ontology = self._ontologies.get(scope.domain)
        ontology.require_known(concept)
        await self._ledger.mark_mastered(scope, concept)
