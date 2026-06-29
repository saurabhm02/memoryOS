"""Port: grade a free-text answer about a concept into a 0–5 assessment.

This is an LLM concern, deliberately separate from the memory engine — Cognee remains
the memory layer; grading is its own provider-agnostic capability (Gemini today,
swappable by config). The core depends only on this Protocol.
"""

from __future__ import annotations

from typing import Protocol

from recallos.core.domain.scoring import AnswerAssessment


class AnswerScorer(Protocol):
    async def score(
        self, *, concept: str, question: str, answer: str
    ) -> AnswerAssessment:
        """Grade ``answer`` to ``question`` about ``concept``. Raises ``ScoringError``
        if a valid assessment cannot be produced."""
        ...
