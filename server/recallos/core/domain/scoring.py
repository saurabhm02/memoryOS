"""The result of grading a learner's free-text answer about one concept.

A pure domain value object — it knows nothing about which LLM produced it. The score is
the only thing that feeds mastery (via the evidence ledger); the rationale and the
demonstrated/missed concept lists are feedback shown to the learner.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AnswerAssessment:
    score: int
    rationale: str
    demonstrated: tuple[str, ...] = ()
    missed: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.score <= 5:
            raise ValueError("score must be between 0 and 5")
