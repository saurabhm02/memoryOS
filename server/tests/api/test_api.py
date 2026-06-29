"""Offline API tests — full HTTP layer over the in-memory doubles (no Cognee/Postgres).

Auth is exercised via dependency overrides: `client` is authenticated (a fake principal),
`unauth_client` has no verifier configured so it proves routes require a token.
"""

import pytest
from fastapi.testclient import TestClient

from recallos.adapters.memory import FakeMemoryEngine
from recallos.adapters.ontology import FileOntologyRepository
from recallos.adapters.persistence import (
    InMemoryEvidenceLedger,
    InMemoryUserRepository,
)
from recallos.adapters.scoring import FakeAnswerScorer
from recallos.api import deps
from recallos.api.app import create_app
from recallos.apps.interview_prep import ONTOLOGY_DIR
from recallos.core.domain.identity import Principal


def _build_app():
    return create_app(
        memory=FakeMemoryEngine(),
        ledger=InMemoryEvidenceLedger(),
        ontologies=FileOntologyRepository(ONTOLOGY_DIR),
        user_repo=InMemoryUserRepository(),
        scorer=FakeAnswerScorer(score=2),
    )


@pytest.fixture
def client():
    app = _build_app()
    app.dependency_overrides[deps.get_principal] = lambda: Principal(
        subject="test-user", email="test@example.com"
    )
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def unauth_client():
    # No verifier configured and no override → every /api/v1 route requires a token.
    with TestClient(_build_app()) as test_client:
        yield test_client


def test_health_is_public(unauth_client):
    response = unauth_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_routes_require_auth(unauth_client):
    assert unauth_client.get("/api/v1/graph").status_code == 401
    assert unauth_client.post("/api/v1/provision").status_code == 401


def test_me_upserts_and_returns_profile(client):
    body = client.get("/api/v1/me").json()
    assert body["subject"] == "test-user"
    assert body["email"] == "test@example.com"
    assert body["tenant_id"] is None


def test_provision(client):
    response = client.post("/api/v1/provision")
    assert response.status_code == 200
    assert response.json()["provisioned"] is True


def test_add_observation_valid(client):
    client.post("/api/v1/provision")
    response = client.post(
        "/api/v1/observations", json={"concept": "Caching", "score": 2}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["concept"] == "Caching"
    assert body["memory_written"] is True


def test_submit_answer_grades_and_remembers(client):
    client.post("/api/v1/provision")
    response = client.post(
        "/api/v1/answers",
        json={
            "concept": "Caching",
            "question": "Explain cache invalidation.",
            "answer": "Caching stores hot data closer to the consumer; invalidation is hard.",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["concept"] == "Caching"
    assert body["score"] == 2
    assert body["memory_written"] is True
    assert "Caching" in body["demonstrated"]


def test_answer_unknown_concept_is_422(client):
    response = client.post(
        "/api/v1/answers", json={"concept": "Kubernetes", "answer": "..."}
    )
    assert response.status_code == 422


def test_answers_require_auth(unauth_client):
    assert (
        unauth_client.post(
            "/api/v1/answers", json={"concept": "Caching", "answer": "x"}
        ).status_code
        == 401
    )


def test_observation_invalid_score_is_422(client):
    response = client.post(
        "/api/v1/observations", json={"concept": "Caching", "score": 6}
    )
    assert response.status_code == 422


def test_observation_unknown_concept_is_422(client):
    response = client.post(
        "/api/v1/observations", json={"concept": "Kubernetes", "score": 3}
    )
    assert response.status_code == 422


def test_diagnosis_flow_finds_root_cause(client):
    client.post("/api/v1/provision")
    for concept, score in [
        ("Caching", 2),
        ("Database Round Trips", 1),
        ("Distributed Transactions", 3),
    ]:
        assert (
            client.post(
                "/api/v1/observations", json={"concept": concept, "score": score}
            ).status_code
            == 200
        )

    body = client.get("/api/v1/diagnosis").json()
    assert body["root_cause"]["concept"] == "Consistency Models"
    assert "Caching" in body["root_cause"]["resolves"]


def test_forget_removes_concept_from_weak_set(client):
    client.post("/api/v1/provision")
    for concept, score in [
        ("Caching", 2),
        ("Database Round Trips", 1),
        ("Distributed Transactions", 3),
        ("Sharding", 2),
    ]:
        client.post("/api/v1/observations", json={"concept": concept, "score": score})

    before = client.get("/api/v1/diagnosis").json()
    assert "Sharding" in before["weak"]

    assert client.post("/api/v1/forget", json={"concept": "Sharding"}).status_code == 200

    after = client.get("/api/v1/diagnosis").json()
    assert "Sharding" not in after["weak"]
    assert after["root_cause"]["concept"] == "Consistency Models"


def test_graph_endpoint_returns_states_edges_and_root_cause(client):
    client.post("/api/v1/provision")
    for concept, score in [
        ("Caching", 2),
        ("Database Round Trips", 1),
        ("Distributed Transactions", 3),
    ]:
        client.post("/api/v1/observations", json={"concept": concept, "score": score})

    body = client.get("/api/v1/graph").json()
    assert len(body["nodes"]) == 15
    states = {node["concept"]: node["state"] for node in body["nodes"]}
    assert states["Caching"] == "weak"
    assert states["Load Balancing"] == "unvisited"
    assert body["root_cause"]["concept"] == "Consistency Models"
    assert any(
        e["source"] == "Consistency Models" and e["target"] == "Caching"
        for e in body["edges"]
    )


def test_improve_returns_delta(client):
    client.post("/api/v1/provision")
    client.post("/api/v1/observations", json={"concept": "Caching", "score": 2})
    response = client.post("/api/v1/improve")
    assert response.status_code == 200
    assert "nodes_after" in response.json()


def test_openapi_documents_v1(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/diagnosis" in paths
    assert "/api/v1/observations" in paths
    assert "/api/v1/forget" in paths
    assert "/api/v1/me" in paths
