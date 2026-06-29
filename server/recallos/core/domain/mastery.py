"""Mastery — the single, honest source of truth for "what is this user weak on".

Mastery is a deterministic, recency-weighted projection over the user's observation
ledger. Recency weighting matters for correctness, not polish: a concept a user
failed early and has since mastered must not stay flagged weak forever. This
replaces the brittle keyword-chunk parsing of the original `weak_set()`.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

MIN_SCORE = 0
MAX_SCORE = 5


@dataclass(frozen=True, slots=True)
class Observation:
    """One scored signal about a concept at a point in time. Domain-level and
    storage-agnostic; how it is persisted is the ledger adapter's concern."""

    concept: str
    score: int
    at: datetime

    def __post_init__(self) -> None:
        if not MIN_SCORE <= self.score <= MAX_SCORE:
            raise ValueError(
                f"score must be {MIN_SCORE}..{MAX_SCORE}, got {self.score!r}"
            )


@dataclass(frozen=True, slots=True)
class MasteryConfig:
    """Tuning for the projection. `recency_half_life` is measured in observations:
    after `half_life` newer attempts, an older attempt carries half the weight. The
    weak-vs-mastered threshold is deliberately NOT here — it is a property of the
    ontology, applied at `MasteryMap.weak_set` time."""

    recency_half_life: float = 5.0


@dataclass(frozen=True, slots=True)
class MasteryMap:
    """Per-concept recency-weighted mastery in the score range. Concepts with no
    observations are simply absent (unknown, not zero)."""

    scores: dict[str, float] = field(default_factory=dict)

    def of(self, concept: str) -> float | None:
        return self.scores.get(concept)

    def weak_set(self, threshold: float) -> set[str]:
        return {c for c, s in self.scores.items() if s < threshold}


class MasteryProjector:
    """Stateless. Projects a stream of observations into a `MasteryMap`."""

    @staticmethod
    def project(
        observations: Iterable[Observation],
        config: MasteryConfig = MasteryConfig(),
    ) -> MasteryMap:
        by_concept: dict[str, list[Observation]] = {}
        for obs in sorted(observations, key=lambda o: o.at):
            by_concept.setdefault(obs.concept, []).append(obs)

        scores = {
            concept: _recency_weighted_mean(obs_list, config.recency_half_life)
            for concept, obs_list in by_concept.items()
        }
        return MasteryMap(scores=scores)


def _recency_weighted_mean(chronological: list[Observation], half_life: float) -> float:
    """`chronological` is oldest-first. The newest observation has weight 1; each
    step older multiplies the weight by 0.5 ** (1 / half_life)."""
    if half_life <= 0:  # degenerate: only the most recent observation counts
        return float(chronological[-1].score)

    weighted_sum = 0.0
    weight_total = 0.0
    for steps_back, obs in enumerate(reversed(chronological)):
        weight = 0.5 ** (steps_back / half_life)
        weighted_sum += weight * obs.score
        weight_total += weight
    return weighted_sum / weight_total
