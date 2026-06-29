"""SCORE — grade a free-text answer, then remember the resulting score.

The graded path that replaces self-reported scores. It validates the concept against the
closed vocabulary *before* spending an LLM call, grades the answer, then routes the score
through the existing RememberObservation (ledger + memory). The deterministic root-cause
machinery is unchanged — only the score's provenance is now an LLM, not the learner.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from recallos.core.application.ports import AnswerScorer, OntologyRepository
from recallos.core.application.usecases.remember_observation import RememberObservation
from recallos.core.domain.identity import UserScope
from recallos.core.domain.scoring import AnswerAssessment


@dataclass(frozen=True, slots=True)
class ScoreAnswerResult:
    assessment: AnswerAssessment
    memory_written: bool


class ScoreAnswer:
    def __init__(
        self,
        scorer: AnswerScorer,
        remember: RememberObservation,
        ontologies: OntologyRepository,
    ) -> None:
        self._scorer = scorer
        self._remember = remember
        self._ontologies = ontologies

    async def execute(
        self,
        scope: UserScope,
        concept: str,
        question: str,
        answer: str,
        at: datetime | None = None,
    ) -> ScoreAnswerResult:
        # Reject an unknown concept before incurring an LLM call.
        self._ontologies.get(scope.domain).require_known(concept)

        assessment = await self._scorer.score(
            concept=concept, question=question, answer=answer
        )
        result = await self._remember.execute(
            scope, concept, assessment.score, at=at or datetime.now(timezone.utc)
        )
        return ScoreAnswerResult(
            assessment=assessment, memory_written=result.memory_written
        )
