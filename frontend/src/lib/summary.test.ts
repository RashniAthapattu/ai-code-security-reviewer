import { describe, expect, it } from "vitest";

import { countBySeverity, sortBySeverity, summaryText } from "./summary";
import type { Finding, Severity } from "./types";

function finding(severity: Severity, line: number): Finding {
  return {
    scanner: "bandit",
    rule_id: "B000",
    title: "Example",
    message: "Example",
    severity,
    confidence: "high",
    line,
    end_line: line,
    snippet: "x",
    cwe: null,
    more_info: null,
    explanation: null,
  };
}

describe("summary", () => {
  it("counts findings by severity", () => {
    const findings = [finding("high", 1), finding("low", 2), finding("low", 3)];
    expect(countBySeverity(findings)).toEqual({ high: 1, medium: 0, low: 2 });
  });

  it("says when nothing was found", () => {
    expect(summaryText([])).toBe("No problems found.");
  });

  it("lists the severities that are present, most serious first", () => {
    const findings = [finding("low", 1), finding("high", 2), finding("low", 3)];
    expect(summaryText(findings)).toBe("3 findings: 1 high, 2 low");
  });

  it("uses the singular for one finding", () => {
    expect(summaryText([finding("medium", 1)])).toBe("1 finding: 1 medium");
  });

  it("sorts by severity, then by line", () => {
    const sorted = sortBySeverity([
      finding("low", 1),
      finding("high", 9),
      finding("high", 4),
      finding("medium", 2),
    ]);
    expect(sorted.map((f) => `${f.severity}:${f.line}`)).toEqual([
      "high:4",
      "high:9",
      "medium:2",
      "low:1",
    ]);
  });
});
