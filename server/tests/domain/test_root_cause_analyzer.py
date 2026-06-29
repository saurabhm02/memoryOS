from recallos.core.domain.competency import PrereqGraph
from recallos.core.domain.diagnosis import RootCauseAnalyzer


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


def test_the_wow_three_weaknesses_trace_to_one_root():
    weak = {"Caching", "Database Round Trips", "Distributed Transactions"}
    result = RootCauseAnalyzer.analyze(_graph(), weak)
    assert result is not None
    assert result.concept == "Consistency Models"
    assert result.resolves == (
        "Caching",
        "Database Round Trips",
        "Distributed Transactions",
    )


def test_empty_weak_set_has_no_root_cause():
    assert RootCauseAnalyzer.analyze(_graph(), set()) is None


def test_weak_concept_with_no_upstream_has_no_root_cause():
    # Nothing is a prerequisite OF Indexing in this graph.
    assert RootCauseAnalyzer.analyze(_graph(), {"Indexing"}) is None


def test_ties_break_alphabetically_for_stable_output():
    graph = PrereqGraph.from_mapping(
        {"Zeta": ["w1"], "Alpha": ["w2"], "w1": [], "w2": []}
    )
    result = RootCauseAnalyzer.analyze(graph, {"w1", "w2"})  # each covers exactly one
    assert result is not None
    assert result.concept == "Alpha"


def test_picks_the_concept_covering_the_most_weaknesses():
    graph = PrereqGraph.from_mapping(
        {
            "Broad": ["a", "b", "c"],
            "Narrow": ["a"],
            "a": [],
            "b": [],
            "c": [],
        }
    )
    result = RootCauseAnalyzer.analyze(graph, {"a", "b", "c"})
    assert result is not None
    assert result.concept == "Broad"
    assert result.resolves == ("a", "b", "c")
