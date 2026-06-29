import { describe, expect, it } from "vitest";

import { classifyState } from "./competency";

describe("classifyState", () => {
  it("maps scores to mastery bands (mirrors the backend)", () => {
    expect(classifyState(null)).toBe("unvisited");
    expect(classifyState(2)).toBe("weak");
    expect(classifyState(3.9)).toBe("weak");
    expect(classifyState(4.2)).toBe("medium");
    expect(classifyState(4.9)).toBe("mastered");
  });

  it("treats an explicit mastery override as mastered regardless of score", () => {
    expect(classifyState(1, true)).toBe("mastered");
  });
});
