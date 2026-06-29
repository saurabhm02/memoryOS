"""The expensive verbs are rate-limited. Enables the limiter just for this test (the
suite disables it globally for determinism — see tests/conftest.py).
"""

from fastapi.testclient import TestClient

from recallos.adapters.memory import FakeMemoryEngine
from recallos.adapters.ontology import FileOntologyRepository
from recallos.adapters.persistence import (
    InMemoryEvidenceLedger,
    InMemoryUserRepository,
)
from recallos.api import deps
from recallos.api.app import create_app
from recallos.api.ratelimit import limiter
from recallos.apps.interview_prep import ONTOLOGY_DIR
from recallos.core.domain.identity import Principal


def test_expensive_routes_are_rate_limited():
    app = create_app(
        memory=FakeMemoryEngine(),
        ledger=InMemoryEvidenceLedger(),
        ontologies=FileOntologyRepository(ONTOLOGY_DIR),
        user_repo=InMemoryUserRepository(),
    )
    app.dependency_overrides[deps.get_principal] = lambda: Principal(subject="rl-user")

    limiter.enabled = True
    try:
        with TestClient(app) as client:
            statuses = [client.post("/api/v1/provision").status_code for _ in range(25)]
        # The 20/minute ceiling on the expensive verb must trip within 25 calls.
        assert 200 in statuses
        assert 429 in statuses
    finally:
        limiter.enabled = False
