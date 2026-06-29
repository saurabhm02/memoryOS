from pathlib import Path

import pytest

from recallos.adapters.ontology import FileOntologyRepository
from recallos.core.domain.errors import (
    OntologyNotFoundError,
    OntologyValidationError,
)

# server/tests/adapters/<this file> -> server/
_BACKEND = Path(__file__).resolve().parents[2]
_ONTOLOGY_DIR = _BACKEND / "recallos" / "apps" / "interview_prep" / "ontologies"


@pytest.fixture
def repo() -> FileOntologyRepository:
    return FileOntologyRepository(_ONTOLOGY_DIR)


def test_loads_backend_sde_ontology(repo: FileOntologyRepository):
    ontology = repo.get("backend_sde")
    assert ontology.domain == "backend_sde"
    assert ontology.version == "1.0.0"
    assert ontology.weak_threshold == 4.0
    assert len(ontology.vocabulary) == 15


def test_consistency_models_is_the_shared_root(repo: FileOntologyRepository):
    ontology = repo.get("backend_sde")
    assert ontology.graph.targets("Consistency Models") == frozenset(
        {"Caching", "Database Round Trips", "Distributed Transactions"}
    )


def test_list_domains_includes_backend_sde(repo: FileOntologyRepository):
    assert "backend_sde" in repo.list_domains()


def test_version_mismatch_is_rejected(repo: FileOntologyRepository):
    with pytest.raises(OntologyValidationError, match="version"):
        repo.get("backend_sde", version="9.9.9")


def test_unknown_domain_raises_not_found(repo: FileOntologyRepository):
    with pytest.raises(OntologyNotFoundError):
        repo.get("does_not_exist")


def test_result_is_cached(repo: FileOntologyRepository):
    assert repo.get("backend_sde") is repo.get("backend_sde")
