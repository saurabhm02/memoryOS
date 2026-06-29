"""Build the competency graph view from the canonical ontology + the durable ledger.

Deterministic and fast: ontology structure + recency-weighted mastery + the
deterministic root cause. The memory engine is not involved — this read never waits on
Cognee, so the hero graph stays instant.
"""

from __future__ import annotations

from recallos.core.application.ports import EvidenceLedger, OntologyRepository
from recallos.core.domain.diagnosis import RootCauseAnalyzer
from recallos.core.domain.graph import CompetencyGraphBuilder, CompetencyGraphView
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import MasteryProjector


class BuildCompetencyGraph:
    def __init__(self, ledger: EvidenceLedger, ontologies: OntologyRepository) -> None:
        self._ledger = ledger
        self._ontologies = ontologies

    async def execute(self, scope: UserScope) -> CompetencyGraphView:
        ontology = self._ontologies.get(scope.domain)
        observations = await self._ledger.observations(scope)
        mastery = MasteryProjector.project(observations)
        mastered = await self._ledger.mastered(scope)
        weak = mastery.weak_set(ontology.weak_threshold) - mastered
        root_cause = RootCauseAnalyzer.analyze(ontology.graph, weak)
        return CompetencyGraphBuilder.build(ontology, mastery, mastered, root_cause)
