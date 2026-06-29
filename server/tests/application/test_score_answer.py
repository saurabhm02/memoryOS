"""ScoreAnswer grades then remembers, and rejects an unknown concept before grading.
Runs over the fake scorer + fake memory + in-memory ledger.
"""

from pathlib import Path

import pytest

from recallos.adapters.memory import FakeMemoryEngine
from recallos.adapters.ontology import FileOntologyRepository
from recallos.adapters.persistence import InMemoryEvidenceLedger
from recallos.adapters.scoring import FakeAnswerScorer
from recallos.core.application.usecases import RememberObservation, ScoreAnswer
from recallos.core.domain.errors import UnknownConceptError
from recallos.core.domain.identity import UserScope

_ONTOLOGY_DIR = (
    Path(__file__).resolve().parents[2]
    / "recallos"
    / "apps"
    / "interview_prep"
    / "ontologies"
)


def _use_case(score: int = 4):
    ontologies = FileOntologyRepository(_ONTOLOGY_DIR)
    ledger = InMemoryEvidenceLedger()
    memory = FakeMemoryEngine()
    remember = RememberObservation(ledger, memory, ontologies)
    return ScoreAnswer(FakeAnswerScorer(score=score), remember, ontologies), ledger


async def test_grades_then_remembers():
    use_case, ledger = _use_case(score=4)
    scope = UserScope(user_id="u1", domain="backend_sde")

    result = await use_case.execute(
        scope, "Caching", "Explain caching", "Caching keeps hot data close."
    )

    assert result.assessment.score == 4
    assert result.memory_written is True
    observations = await ledger.observations(scope)
    assert len(observations) == 1 and observations[0].score == 4


async def test_rejects_unknown_concept_before_grading():
    use_case, ledger = _use_case()
    scope = UserScope(user_id="u1", domain="backend_sde")

    with pytest.raises(UnknownConceptError):
        await use_case.execute(scope, "Kubernetes", "Q", "an answer")

    assert await ledger.observations(scope) == []
