import pytest

from recallos.core.domain.competency import PrereqGraph
from recallos.core.domain.errors import OntologyValidationError


def _graph() -> PrereqGraph:
    return PrereqGraph.from_mapping(
        {
            "Consistency Models": [
                "Caching",
                "Database Round Trips",
                "Distributed Transactions",
            ],
            "Caching": [],
            "Database Round Trips": [],
            "Distributed Transactions": [],
            "Indexing": ["Database Round Trips"],
        }
    )


def test_concepts_lists_every_node():
    graph = _graph()
    assert graph.concepts == frozenset(
        {
            "Consistency Models",
            "Caching",
            "Database Round Trips",
            "Distributed Transactions",
            "Indexing",
        }
    )


def test_targets_are_downstream_dependents():
    graph = _graph()
    assert graph.targets("Consistency Models") == frozenset(
        {"Caching", "Database Round Trips", "Distributed Transactions"}
    )
    assert graph.targets("Caching") == frozenset()


def test_prerequisites_are_upstream_concepts():
    graph = _graph()
    # Both Consistency Models and Indexing are prerequisites of Database Round Trips.
    assert graph.prerequisites("Database Round Trips") == frozenset(
        {"Consistency Models", "Indexing"}
    )
    assert graph.prerequisites("Consistency Models") == frozenset()


def test_dangling_edge_is_rejected():
    with pytest.raises(OntologyValidationError, match="unknown concept"):
        PrereqGraph.from_mapping({"A": ["B"]})  # B is not a node


def test_cycle_is_rejected():
    with pytest.raises(OntologyValidationError, match="cycle"):
        PrereqGraph.from_mapping({"A": ["B"], "B": ["A"]})


def test_self_loop_is_a_cycle():
    with pytest.raises(OntologyValidationError, match="cycle"):
        PrereqGraph.from_mapping({"A": ["A"]})
