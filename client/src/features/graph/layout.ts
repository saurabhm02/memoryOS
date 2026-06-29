import dagre from "@dagrejs/dagre";
import { type Edge, Position } from "@xyflow/react";

import {
  CONCEPT_NODE_HEIGHT,
  CONCEPT_NODE_WIDTH,
  type ConceptFlowNode,
} from "./ConceptNode";

/** Lay out the competency DAG top-down (prerequisites above their dependents) with
 * dagre. React Flow does not position nodes itself, so we compute coordinates here. */
export function layoutGraph(nodes: ConceptFlowNode[], edges: Edge[]): ConceptFlowNode[] {
  const graph = new dagre.graphlib.Graph();
  graph.setGraph({ rankdir: "TB", ranksep: 72, nodesep: 26, marginx: 16, marginy: 16 });
  graph.setDefaultEdgeLabel(() => ({}));

  nodes.forEach((node) =>
    graph.setNode(node.id, { width: CONCEPT_NODE_WIDTH, height: CONCEPT_NODE_HEIGHT }),
  );
  edges.forEach((edge) => graph.setEdge(edge.source, edge.target));

  dagre.layout(graph);

  return nodes.map((node) => {
    const { x, y } = graph.node(node.id);
    return {
      ...node,
      position: { x: x - CONCEPT_NODE_WIDTH / 2, y: y - CONCEPT_NODE_HEIGHT / 2 },
      targetPosition: Position.Top,
      sourcePosition: Position.Bottom,
    };
  });
}
