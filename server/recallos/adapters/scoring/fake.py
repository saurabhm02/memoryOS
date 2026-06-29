"""FakeAnswerScorer — deterministic test double for the AnswerScorer port.

Returns a fixed score with feedback derived from the concept, so application/API tests
exercise the graded path with no LLM. Production grades on GeminiAnswerScorer.
"""

from __future__ import annotations

from recallos.core.domain.scoring import AnswerAssessment


class FakeAnswerScorer:
    def __init__(self, score: int = 3) -> None:
        self._score = score

    async def score(
        self, *, concept: str, question: str, answer: str
    ) -> AnswerAssessment:
        return AnswerAssessment(
            score=self._score,
            rationale=f"Assessed the answer on '{concept}'.",
            demonstrated=(concept,),
            missed=(),
        )
