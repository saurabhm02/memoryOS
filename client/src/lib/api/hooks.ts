import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { classifyState } from "../competency";
import { api } from "./client";
import { queryKeys } from "./keys";
import type { CompetencyGraph, Scope } from "./schemas";

/** The competency graph — the hero read. Fast and deterministic on the server. */
export function useGraph(scope: Scope, enabled = true) {
  return useQuery({
    queryKey: queryKeys.graph(scope),
    queryFn: () => api.graph(scope),
    enabled,
  });
}

/** Recall: weak set + root cause + graph-grounded narration. */
export function useDiagnosis(scope: Scope, enabled = true) {
  return useQuery({
    queryKey: queryKeys.diagnosis(scope),
    queryFn: () => api.diagnosis(scope),
    enabled,
  });
}

function invalidateScope(qc: ReturnType<typeof useQueryClient>, scope: Scope) {
  void qc.invalidateQueries({ queryKey: queryKeys.graph(scope) });
  void qc.invalidateQueries({ queryKey: queryKeys.diagnosis(scope) });
}

export function useProvision(scope: Scope) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.provision(scope),
    onSuccess: () => invalidateScope(qc, scope),
  });
}

/**
 * Remember an observation. The graph updates optimistically the instant the user
 * submits (so it visibly evolves while Cognee cognifies in the background, ~20–40s),
 * then reconciles with the server's recency-weighted truth on settle.
 */
export function useObserve(scope: Scope) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { concept: string; score: number }) => api.observe(scope, body),
    onMutate: async (body) => {
      await qc.cancelQueries({ queryKey: queryKeys.graph(scope) });
      const previous = qc.getQueryData<CompetencyGraph>(queryKeys.graph(scope));
      if (previous) {
        qc.setQueryData<CompetencyGraph>(queryKeys.graph(scope), {
          ...previous,
          nodes: previous.nodes.map((node) =>
            node.concept === body.concept
              ? { ...node, score: body.score, state: classifyState(body.score) }
              : node,
          ),
        });
      }
      return { previous };
    },
    onError: (_error, _body, context) => {
      if (context?.previous) {
        qc.setQueryData(queryKeys.graph(scope), context.previous);
      }
    },
    onSettled: () => invalidateScope(qc, scope),
  });
}

/**
 * Submit a free-text answer for LLM grading, then remember the score. Unlike the manual
 * path, the score isn't known until the model responds, so there's no optimistic recolor;
 * the graph reconciles with the server's truth once the grade settles.
 */
export function useScoreAnswer(scope: Scope) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { concept: string; question: string; answer: string }) =>
      api.scoreAnswer(scope, body),
    onSettled: () => invalidateScope(qc, scope),
  });
}

export function useImprove(scope: Scope) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.improve(scope),
    onSettled: () => invalidateScope(qc, scope),
  });
}

export function useForget(scope: Scope) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (concept: string) => api.forget(scope, concept),
    onMutate: async (concept) => {
      await qc.cancelQueries({ queryKey: queryKeys.graph(scope) });
      const previous = qc.getQueryData<CompetencyGraph>(queryKeys.graph(scope));
      if (previous) {
        qc.setQueryData<CompetencyGraph>(queryKeys.graph(scope), {
          ...previous,
          nodes: previous.nodes.map((node) =>
            node.concept === concept ? { ...node, state: "mastered" } : node,
          ),
        });
      }
      return { previous };
    },
    onError: (_error, _concept, context) => {
      if (context?.previous) {
        qc.setQueryData(queryKeys.graph(scope), context.previous);
      }
    },
    onSettled: () => invalidateScope(qc, scope),
  });
}
