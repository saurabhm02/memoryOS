from recallos.core.domain.competency import Ontology, PrereqGraph
from recallos.core.domain.diagnosis import RootCause
from recallos.core.domain.graph import CompetencyGraphBuilder, classify_state
from recallos.core.domain.mastery import MasteryMap


def _ontology() -> Ontology:
    graph = PrereqGraph.from_mapping({"Consistency Models": ["Caching"], "Caching": []})
    return Ontology(domain="t", version="1", title="T", weak_threshold=4.0, graph=graph)


def test_classify_state_bands():
    assert classify_state(None, mastered=False, weak_threshold=4.0) == "unvisited"
    assert classify_state(2.0, mastered=False, weak_threshold=4.0) == "weak"
    assert classify_state(4.2, mastered=False, weak_threshold=4.0) == "medium"
    assert classify_state(4.9, mastered=False, weak_threshold=4.0) == "mastered"
    # An explicit mastery override always wins, regardless of score.
    assert classify_state(1.0, mastered=True, weak_threshold=4.0) == "mastered"


def test_builder_assembles_nodes_edges_and_root_cause():
    view = CompetencyGraphBuilder.build(
        _ontology(),
        MasteryMap(scores={"Caching": 2.0}),
        set(),
        RootCause(concept="Consistency Models", resolves=("Caching",)),
    )
    states = {node.concept: node.state for node in view.nodes}
    assert states["Caching"] == "weak"
    assert states["Consistency Models"] == "unvisited"  # no observations yet
    assert any(
        e.source == "Consistency Models" and e.target == "Caching" for e in view.edges
    )
    assert view.root_cause is not None
    assert view.root_cause.concept == "Consistency Models"


def test_mastery_override_shows_as_mastered():
    view = CompetencyGraphBuilder.build(
        _ontology(),
        MasteryMap(scores={"Caching": 1.0}),
        {"Caching"},
        None,
    )
    states = {node.concept: node.state for node in view.nodes}
    assert states["Caching"] == "mastered"
