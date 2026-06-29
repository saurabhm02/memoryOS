import { useEffect, useState } from "react";
import { toast } from "sonner";

import { RememberingIndicator } from "@/components/RememberingIndicator";
import { ErrorState } from "@/components/states";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CompetencyGraph } from "@/features/graph";
import { ForgetDialog } from "@/features/memory/ForgetDialog";
import { MemoryTimeline } from "@/features/memory/MemoryTimeline";
import {
  type MemorySnapshot,
  getHistory,
  recordSnapshot,
  snapshotOf,
} from "@/features/memory/memoryHistory";
import { useForget, useGraph, useImprove } from "@/lib/api/hooks";
import { useScope } from "@/lib/scope";

export function MemoryScreen() {
  const scope = useScope();
  const graph = useGraph(scope);
  const improve = useImprove(scope);
  const forget = useForget(scope);
  const [history, setHistory] = useState<MemorySnapshot[]>(() =>
    getHistory(scope.userId),
  );

  useEffect(() => {
    if (graph.data) {
      setHistory(recordSnapshot(scope.userId, snapshotOf(graph.data)));
    }
  }, [graph.data, scope.userId]);

  const handleImprove = () =>
    improve.mutate(undefined, {
      onSuccess: (delta) =>
        toast.success("Memory improved", {
          description: delta.derived_patterns.length
            ? `Pattern ${delta.derived_patterns.join(", ")} derived.`
            : "Cognee enriched your knowledge graph.",
        }),
      onError: () =>
        toast.error("Improve failed", {
          description: "Couldn't reach the memory engine.",
        }),
    });

  const handleForget = (concept: string) =>
    forget.mutate(concept, {
      onSuccess: () =>
        toast.success("Forgotten", {
          description: `${concept} left your active plan.`,
        }),
      onError: () =>
        toast.error("Forget failed", {
          description: "Couldn't reach the memory engine.",
        }),
    });

  const pendingConcept = forget.isPending ? (forget.variables ?? null) : null;

  return (
    <div className="flex h-full flex-col">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border px-5 py-4 sm:px-6">
        <div>
          <h1 className="text-lg font-semibold tracking-tight text-ink">Memory</h1>
          <p className="text-[13px] text-ink-muted">
            Your competency graph, accumulated across every session.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {improve.isPending && <RememberingIndicator label="Improving memory" />}
          <ForgetDialog
            graph={graph.data ?? null}
            onForget={handleForget}
            pendingConcept={pendingConcept}
          />
          <Button onClick={handleImprove} disabled={improve.isPending}>
            {improve.isPending ? "Improving…" : "Improve memory"}
          </Button>
        </div>
      </header>

      <div className="flex min-h-0 flex-1 flex-col gap-5 overflow-auto p-5 sm:p-6">
        <MemoryTimeline history={history} />
        <div className="min-h-[420px] flex-1 overflow-hidden rounded-lg border border-border bg-surface">
          {graph.isLoading ? (
            <Skeleton className="h-full w-full" />
          ) : graph.isError ? (
            <ErrorState onRetry={() => void graph.refetch()} />
          ) : graph.data ? (
            <CompetencyGraph data={graph.data} />
          ) : null}
        </div>
      </div>
    </div>
  );
}
