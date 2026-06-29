from datetime import datetime, timedelta

import pytest

from recallos.core.domain.mastery import (
    MasteryConfig,
    MasteryProjector,
    Observation,
)

_BASE = datetime(2026, 1, 1)


def _obs(concept: str, score: int, day: int) -> Observation:
    return Observation(concept=concept, score=score, at=_BASE + timedelta(days=day))


def test_observation_rejects_out_of_range_score():
    with pytest.raises(ValueError):
        Observation(concept="Caching", score=6, at=_BASE)


def test_persistent_weakness_stays_weak():
    obs = [_obs("Caching", 1, day) for day in range(4)]
    mastery = MasteryProjector.project(obs)
    assert mastery.of("Caching") == pytest.approx(1.0)
    assert "Caching" in mastery.weak_set(threshold=4.0)


def test_recent_recovery_beats_plain_mean():
    # Two early failures, two recent strong answers.
    obs = [
        _obs("Caching", 1, 0),
        _obs("Caching", 1, 1),
        _obs("Caching", 5, 2),
        _obs("Caching", 5, 3),
    ]
    plain_mean = (1 + 1 + 5 + 5) / 4
    mastery = MasteryProjector.project(obs)
    # Recency weighting pulls the score toward the recent 5s, above the plain mean.
    assert mastery.of("Caching") > plain_mean


def test_recent_strong_mastery_clears_old_failures():
    # Two early failures, then a sustained run of recent perfect answers: a
    # recency-weighted projection should no longer flag this concept as weak.
    obs = [
        _obs("Indexing", 0, 0),
        _obs("Indexing", 0, 1),
        _obs("Indexing", 5, 5),
        _obs("Indexing", 5, 6),
        _obs("Indexing", 5, 7),
        _obs("Indexing", 5, 8),
    ]
    mastery = MasteryProjector.project(obs, MasteryConfig(recency_half_life=2.0))
    assert "Indexing" not in mastery.weak_set(threshold=4.0)


def test_weak_set_filters_by_threshold():
    mastery = MasteryProjector.project([_obs("A", 5, 0), _obs("B", 1, 0)])
    assert mastery.weak_set(threshold=4.0) == {"B"}


def test_unobserved_concept_is_absent_not_zero():
    mastery = MasteryProjector.project([_obs("A", 3, 0)])
    assert mastery.of("Unseen") is None
