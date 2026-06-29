"""The competency graph view — the data the UI's hero visualization renders.

Pure domain: assembles the authored ontology structure + per-concept mastery state +
the diagnosed root cause into one view. No I/O, no engine. The mastery *bands* here add
graph granularity (mastered/medium) on top of the binary weak threshold the root-cause
decision uses, so the graph can show progress filling in across sessions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .competency import Ontology
from .diagnosis import RootCause
from .mastery import MasteryMap

CompetencyState = Literal["unvisited", "weak", "medium", "mastered"]

# Score margin above the ontology's weak threshold that reads as fully mastered.
_MASTERED_MARGIN = 0.6


def classify_state(
    score: float | None, *, mastered: bool, weak_threshold: float
) -> CompetencyState:
    """Map a concept's recency-weighted score to a display state. An explicit mastery
    override (the Forget verb) always wins; an unobserved concept is unvisited."""
    if mastered:
        return "mastered"
    if score is None:
        return "unvisited"
    if score < weak_threshold:
        return "weak"
    if score >= weak_threshold + _MASTERED_MARGIN:
        return "mastered"
    return "medium"


@dataclass(frozen=True, slots=True)
class GraphNode:
    concept: str
    state: CompetencyState
    score: float | None  # recency-weighted mastery, None if unobserved


@dataclass(frozen=True, slots=True)
class GraphEdge:
    source: str  # the prerequisite concept
    target: str  # the concept that depends on it


@dataclass(frozen=True, slots=True)
class CompetencyGraphView:
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    root_cause: RootCause | None


class CompetencyGraphBuilder:
    """Stateless."""

    @staticmethod
    def build(
        ontology: Ontology,
        mastery: MasteryMap,
        mastered: set[str],
        root_cause: RootCause | None,
    ) -> CompetencyGraphView:
        nodes = tuple(
            GraphNode(
                concept=concept,
                state=classify_state(
                    mastery.of(concept),
                    mastered=concept in mastered,
                    weak_threshold=ontology.weak_threshold,
                ),
                score=mastery.of(concept),
            )
            for concept in sorted(ontology.vocabulary)
        )
        edges = tuple(
            GraphEdge(source=src, target=tgt)
            for src in sorted(ontology.graph.concepts)
            for tgt in sorted(ontology.graph.targets(src))
        )
        return CompetencyGraphView(nodes=nodes, edges=edges, root_cause=root_cause)
