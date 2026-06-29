import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { RootCauseCallout } from "./RootCauseCallout";

describe("RootCauseCallout", () => {
  it("states the insight, the converging concepts, and the narration", () => {
    render(
      <RootCauseCallout
        rootCause="Consistency Models"
        resolves={["Caching", "Database Round Trips", "Distributed Transactions"]}
        narration="You keep missing these three."
      />,
    );

    expect(
      screen.getByRole("heading", { name: /Consistency Models/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/You keep missing these three\./i)).toBeInTheDocument();
    expect(screen.getByText("Caching")).toBeInTheDocument();
    expect(screen.getByText("Distributed Transactions")).toBeInTheDocument();
  });
});
