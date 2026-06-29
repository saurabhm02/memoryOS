"""Live API smoke against the production wiring (real Cognee + Gemini + Aiven Postgres).

Marked ``integration``. A single ``TestClient`` context runs everything on one event
loop (as a real server does), keeping Cognee's loop-bound locks valid. Auth is overridden
with a fixed principal (we don't mint a real OIDC token here). Run with the sandbox
disabled, in its own process:

    pytest tests/api/test_api_integration.py -m integration -o addopts=""
"""

import pytest
from fastapi.testclient import TestClient

from recallos.api import deps
from recallos.core.domain.identity import Principal

pytestmark = pytest.mark.integration


@pytest.fixture
def live_client():
    from recallos.api.app import create_app

    app = create_app()  # real adapters, built in the lifespan
    app.dependency_overrides[deps.get_principal] = lambda: Principal(
        subject="api_e2e_user", email="api_e2e@example.com"
    )
    with TestClient(app) as test_client:
        yield test_client


def test_live_api_full_flow(live_client):
    assert live_client.get("/health").json()["status"] == "ok"
    assert live_client.post("/api/v1/provision").status_code == 200

    for concept, score in [
        ("Caching", 2),
        ("Database Round Trips", 1),
        ("Distributed Transactions", 3),
    ]:
        response = live_client.post(
            "/api/v1/observations", json={"concept": concept, "score": score}
        )
        assert response.status_code == 200
        assert response.json()["memory_written"] is True

    diagnosis = live_client.get("/api/v1/diagnosis").json()
    assert diagnosis["root_cause"]["concept"] == "Consistency Models"

    # LLM grading (real Gemini): a free-text answer is scored 0–5 and remembered.
    graded = live_client.post(
        "/api/v1/answers",
        json={
            "concept": "Caching",
            "question": "Explain cache invalidation strategies and their trade-offs.",
            "answer": (
                "Use TTL expiry for simplicity, write-through to keep the cache and DB "
                "consistent, and write-back for throughput at the cost of durability. "
                "Invalidation is hard because of staleness across replicas."
            ),
        },
    )
    assert graded.status_code == 200
    body = graded.json()
    assert 0 <= body["score"] <= 5
    assert body["memory_written"] is True
