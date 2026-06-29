import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { type Mock, beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("@/features/graph", () => ({
  CompetencyGraph: () => <div data-testid="graph" />,
}));
vi.mock("@/lib/api/client", () => ({
  api: {
    graph: vi.fn(),
    diagnosis: vi.fn(),
    provision: vi.fn(),
    scoreAnswer: vi.fn(),
  },
}));

import { api } from "@/lib/api/client";
import { renderWithProviders } from "@/test/utils";

import { SessionScreen } from "./SessionScreen";

const asMock = (fn: unknown) => fn as unknown as Mock;

function setUser(started: boolean) {
  if (started) localStorage.setItem("recallos.started.test-user", "1");
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});

describe("SessionScreen", () => {
  it("onboards a new learner and provisions on Begin", async () => {
    setUser(false);
    asMock(api.graph).mockResolvedValue({ nodes: [], edges: [], root_cause: null });
    asMock(api.diagnosis).mockResolvedValue({
      weak: [],
      root_cause: null,
      narration: null,
    });
    asMock(api.provision).mockResolvedValue({ provisioned: true });

    renderWithProviders(<SessionScreen />);

    await userEvent.click(
      await screen.findByRole("button", { name: /begin a session/i }),
    );
    await waitFor(() => expect(api.provision).toHaveBeenCalled());
  });

  it("surfaces the root cause and grades a submitted answer", async () => {
    setUser(true);
    asMock(api.graph).mockResolvedValue({
      nodes: [{ concept: "Consistency Models", state: "unvisited", score: null }],
      edges: [],
      root_cause: {
        concept: "Consistency Models",
        resolves: ["Caching", "Database Round Trips", "Distributed Transactions"],
      },
    });
    asMock(api.diagnosis).mockResolvedValue({
      weak: ["Caching"],
      root_cause: { concept: "Consistency Models", resolves: ["Caching"] },
      narration: "These trace upstream.",
    });
    asMock(api.scoreAnswer).mockResolvedValue({
      concept: "Consistency Models",
      score: 3,
      rationale: "Solid grasp of read-your-writes.",
      demonstrated: ["read-your-writes"],
      missed: ["quorums"],
      memory_written: true,
    });

    renderWithProviders(<SessionScreen />);

    expect(
      await screen.findByRole("heading", { name: /Consistency Models/i }),
    ).toBeInTheDocument();

    await userEvent.type(
      screen.getByLabelText("Your answer"),
      "Read-your-writes means a session sees its own updates.",
    );
    await userEvent.click(screen.getByRole("button", { name: /submit answer/i }));

    await waitFor(() =>
      expect(api.scoreAnswer).toHaveBeenCalledWith(
        { userId: "test-user", domain: "backend_sde" },
        expect.objectContaining({
          concept: "Consistency Models",
          answer: expect.stringContaining("Read-your-writes"),
        }),
      ),
    );

    // The LLM grade is shown back to the learner.
    expect(
      await screen.findByText(/Solid grasp of read-your-writes/i),
    ).toBeInTheDocument();
  });
});
