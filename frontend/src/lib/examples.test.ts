import { describe, expect, it } from "vitest";

import { EXAMPLES, MAX_CODE_LENGTH } from "./examples";

describe("examples", () => {
  it("has an example for every language", () => {
    expect(Object.keys(EXAMPLES).sort()).toEqual([
      "javascript",
      "python",
      "typescript",
    ]);
  });

  it("keeps each example within the size limit", () => {
    for (const code of Object.values(EXAMPLES)) {
      expect(code.trim().length).toBeGreaterThan(0);
      expect(code.length).toBeLessThan(MAX_CODE_LENGTH);
    }
  });
});
