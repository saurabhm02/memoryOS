import { Handle, type Node, type NodeProps, Position } from "@xyflow/react";
import { Star } from "lucide-react";

import type { CompetencyState } from "@/lib/api/schemas";
import { STATE_META } from "@/lib/competency";
import { cn } from "@/lib/utils";

export interface ConceptNodeData {
  concept: string;
  state: CompetencyState;
  score: number | null;
  isRootCause: boolean;
  // React Flow v12 requires node data to be an index-signature record.
  [key: string]: unknown;
}

export type ConceptFlowNode = Node<ConceptNodeData, "concept">;

export const CONCEPT_NODE_WIDTH = 184;
export const CONCEPT_NODE_HEIGHT = 48;

const handleClass = "!h-1.5 !w-1.5 !border-0 !bg-border-strong";

export function ConceptNode({ data }: NodeProps<ConceptFlowNode>) {
  const meta = STATE_META[data.state];
  const stateColor = `var(${meta.cssVar})`;
  const tinted = data.state !== "unvisited";

  return (
    <div
      tabIndex={0}
      role="group"
      aria-label={`${data.concept}. ${meta.label}${
        data.isRootCause ? ". Root cause." : ""
      }${data.score !== null ? ` Mastery ${data.score.toFixed(1)} of 5.` : ""}`}
      className={cn(
        "relative flex items-center gap-2.5 rounded-md border px-3 py-2 transition-shadow duration-200",
        data.isRootCause
          ? "border-root-cause shadow-root-cause"
          : "border-border hover:border-border-strong",
      )}
      style={{
        width: CONCEPT_NODE_WIDTH,
        height: CONCEPT_NODE_HEIGHT,
        backgroundColor: tinted
          ? `color-mix(in oklch, ${stateColor} 12%, var(--surface-2))`
          : "var(--surface-2)",
      }}
    >
      <Handle type="target" position={Position.Top} className={handleClass} />

      <span
        aria-hidden
        className="h-2.5 w-2.5 shrink-0 rounded-full ring-1 ring-inset ring-black/20"
        style={{ backgroundColor: stateColor }}
      />
      <span className="truncate font-mono text-[13px] leading-tight text-ink">
        {data.concept}
      </span>
      {data.score !== null && (
        <span className="ml-auto font-mono text-[11px] tabular-nums text-ink-muted">
          {data.score.toFixed(1)}
        </span>
      )}

      {data.isRootCause && (
        <span
          aria-hidden
          className="absolute -right-2 -top-2 grid h-5 w-5 place-items-center rounded-full bg-root-cause text-bg"
        >
          <Star className="h-3 w-3" fill="currentColor" strokeWidth={0} />
        </span>
      )}

      <Handle type="source" position={Position.Bottom} className={handleClass} />
    </div>
  );
}
