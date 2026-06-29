"""ResetLearnerMemory clears one scope's ledger + memory and nothing else — the engine
behind the demo-reset script. Runs over the fake memory engine + in-memory ledger.
"""

from datetime import datetime
from pathlib import Path

from recallos.adapters.memory import FakeMemoryEngine
from recallos.adapters.ontology import FileOntologyRepository
from recallos.adapters.persistence import (
    InMemoryEvidenceLedger,
    InMemoryUserRepository,
)
from recallos.core.application.usecases import (
    RememberObservation,
    ResetLearnerMemory,
)
from recallos.core.domain.identity import UserScope

_ONTOLOGY_DIR = (
    Path(__file__).resolve().parents[2]
    / "recallos"
    / "apps"
    / "interview_prep"
    / "ontologies"
)


async def test_reset_clears_demo_scope_but_preserves_others():
    ontologies = FileOntologyRepository(_ONTOLOGY_DIR)
    ledger = InMemoryEvidenceLedger()
    memory = FakeMemoryEngine()
    demo = UserScope(user_id="demo", domain="backend_sde")
    other = UserScope(user_id="other", domain="backend_sde")

    remember = RememberObservation(ledger, memory, ontologies)
    await remember.execute(demo, "Caching", 2, at=datetime(2026, 1, 1))
    await remember.execute(other, "Caching", 2, at=datetime(2026, 1, 1))
    await ledger.mark_mastered(demo, "Indexing")

    await ResetLearnerMemory(memory, ledger).execute(demo)

    assert await ledger.observations(demo) == []
    assert await ledger.mastered(demo) == set()
    # Another learner's data is untouched.
    assert len(await ledger.observations(other)) == 1


async def test_user_repo_resolves_subject_by_email():
    users = InMemoryUserRepository()
    await users.upsert("sub-1", "demo@recallos.app")

    found = await users.get_by_email("demo@recallos.app")
    assert found is not None and found.subject == "sub-1"
    assert await users.get_by_email("nobody@example.com") is None
