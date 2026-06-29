"""GeminiAnswerScorer parses strict JSON, clamps the score, and turns any failure into
ScoringError — verified with an injected completion (no network).
"""

import json

import pytest

from recallos.adapters.scoring import GeminiAnswerScorer
from recallos.core.domain.errors import ScoringError


def _scorer(payload):
    async def completion(_messages):
        return payload

    return GeminiAnswerScorer(completion=completion)


async def test_parses_and_clamps_score():
    scorer = _scorer(
        json.dumps(
            {
                "score": 9,  # out of range → clamped to 5
                "rationale": "Strong answer.",
                "demonstrated": ["TTL", "eviction"],
                "missed": ["write-through"],
            }
        )
    )
    assessment = await scorer.score(concept="Caching", question="Q", answer="ans")
    assert assessment.score == 5
    assert assessment.rationale == "Strong answer."
    assert assessment.demonstrated == ("TTL", "eviction")
    assert assessment.missed == ("write-through",)


async def test_empty_answer_raises_before_calling_llm():
    scorer = _scorer("never used")
    with pytest.raises(ScoringError):
        await scorer.score(concept="Caching", question="Q", answer="   ")


async def test_malformed_json_raises_scoring_error():
    scorer = _scorer("not json at all")
    with pytest.raises(ScoringError):
        await scorer.score(concept="Caching", question="Q", answer="ans")
