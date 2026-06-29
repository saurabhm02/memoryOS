import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";

vi.mock("./client", () => ({
  api: {
    observe: vi.fn(() => new Promise<never>(() => {})), // never resolves → stays optimistic
    graph: vi.fn(),
    diagnosis: vi.fn(),
    provision: vi.fn(),
    improve: vi.fn(),
    forget: vi.fn(),
  },
}));

import { useObserve } from "./hooks";
import { queryKeys } from "./keys";
import type { CompetencyGraph, Scope } from "./schemas";

const scope: Scope = { userId: "u", domain: "backend_sde" };

function wrapper(client: QueryClient) {
  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
}

describe("useObserve", () => {
  it("optimistically recolors the submitted concept while the write is in flight", async () => {
    const client = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    const initial: CompetencyGraph = {
      nodes: [{ concept: "Caching", state: "unvisited", score: null }],
      edges: [],
      root_cause: null,
    };
    client.setQueryData(queryKeys.graph(scope), initial);

    const { result } = renderHook(() => useObserve(scope), {
      wrapper: wrapper(client),
    });
    act(() => {
      result.current.mutate({ concept: "Caching", score: 2 });
    });

    await waitFor(() => {
      const graph = client.getQueryData<CompetencyGraph>(queryKeys.graph(scope));
      expect(graph?.nodes[0].state).toBe("weak");
      expect(graph?.nodes[0].score).toBe(2);
    });
  });
});
