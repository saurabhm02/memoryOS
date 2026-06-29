import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { PracticePanel } from "./PracticePanel";

describe("PracticePanel", () => {
  it("requires a non-empty answer before submitting, then reports the answer", async () => {
    const onSubmit = vi.fn();
    render(
      <PracticePanel
        concept="Caching"
        question="Explain cache invalidation."
        isPending={false}
        onSubmit={onSubmit}
      />,
    );

    const submit = screen.getByRole("button", { name: /submit answer/i });
    expect(submit).toBeDisabled();

    await userEvent.type(
      screen.getByLabelText("Your answer"),
      "Caching keeps hot data close to the consumer.",
    );
    expect(submit).toBeEnabled();

    await userEvent.click(submit);
    expect(onSubmit).toHaveBeenCalledWith(
      "Caching keeps hot data close to the consumer.",
    );
  });

  it("shows the remembering affordance while pending", () => {
    render(
      <PracticePanel concept="Caching" question="Q?" isPending onSubmit={() => {}} />,
    );
    expect(screen.getByText(/remembering/i)).toBeInTheDocument();
  });
});
