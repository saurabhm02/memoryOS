import "@xyflow/react/dist/style.css";

import {
  Background,
  BackgroundVariant,
  Controls,
  type Edge,
  ReactFlow,
} from "@xyflow/react";
import { useMemo } from "react";

import type {
  CompetencyGraph as CompetencyGraphData,
  CompetencyState,
} from "@/lib/api/schemas";
import { STATE_META } from "@/lib/competency";
import { prefersReducedMotion } from "@/lib/motion";

import { ConceptNode, type ConceptFlowNode } from "./ConceptNode";
import { layoutGraph } from "./layout";

const nodeTypes = { concept: ConceptNode };
const LEGEND: CompetencyState[] = ["weak", "medium", "mastered", "unvisited"];

function Legend() {
  return (
    <ul className="pointer-events-none absolute left-3 top-3 z-10 flex flex-wrap gap-x-3 gap-y-1.5 text-[11px] text-ink-muted">
      {LEGEND.map((state) => (
        <li key={state} className="inline-flex items-center gap-1.5">
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: `var(${STATE_META[state].cssVar})` }}
            aria-hidden
          />
          {STATE_META[state].label}
        </li>
      ))}
    </ul>
  );
}

interface CompetencyGraphProps {
  data: CompetencyGraphData;
  className?: string;
}

/**
 * The hero visualization. Renders the prerequisite DAG, colored by per-concept mastery,
 * with the diagnosed root cause ringed in amber and the traversal path from it to the
 * weaknesses it explains highlighted and animated.
 */
export function CompetencyGraph({ data, className }: CompetencyGraphProps) {
  const { nodes, edges } = useMemo(() => buildFlow(data), [data]);

  return (
    <div
      className={className}
      style={{ position: "relative", height: "100%", width: "100%" }}
      role="region"
      aria-label="Competency graph — concepts colored by mastery, with the root cause ringed"
    >
      <Legend />
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        colorMode="dark"
        fitView
        fitViewOptions={{ padding: 0.18 }}
        nodesDraggable={false}
        nodesConnectable={false}
        edgesFocusable={false}
        minZoom={0.4}
        maxZoom={1.6}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={22}
          size={1}
          color="var(--border)"
        />
        <Controls showInteractive={false} position="bottom-right" />
      </ReactFlow>
    </div>
  );
}

function buildFlow(data: CompetencyGraphData): {
  nodes: ConceptFlowNode[];
  edges: Edge[];
} {
  const rootConcept = data.root_cause?.concept ?? null;
  const resolves = new Set(data.root_cause?.resolves ?? []);
  const animate = !prefersReducedMotion();

  const baseNodes: ConceptFlowNode[] = data.nodes.map((node) => ({
    id: node.concept,
    type: "concept",
    position: { x: 0, y: 0 },
    data: {
      concept: node.concept,
      state: node.state,
      score: node.score,
      isRootCause: node.concept === rootConcept,
    },
  }));

  const edges: Edge[] = data.edges.map((edge) => {
    const onPath = edge.source === rootConcept && resolves.has(edge.target);
    return {
      id: `${edge.source}->${edge.target}`,
      source: edge.source,
      target: edge.target,
      animated: onPath && animate,
      style: {
        stroke: onPath ? "var(--root-cause)" : "var(--border-strong)",
        strokeWidth: onPath ? 2 : 1,
        opacity: onPath ? 1 : 0.7,
      },
    };
  });

  return { nodes: layoutGraph(baseNodes, edges), edges };
}
