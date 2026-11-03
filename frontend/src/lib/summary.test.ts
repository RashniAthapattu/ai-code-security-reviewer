import { describe, expect, it } from "vitest";

import {
  aiNotice,
  countBySeverity,
  sortBySeverity,
  summaryText,
} from "./summary";
import type { AIStatus, Finding, ScanResult, Severity } from "./types";

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

function scanResult(ai_status: AIStatus, ai_message: string | null): ScanResult {
  return { findings: [], errors: [], ai_status, ai_message };
}

describe("aiNotice", () => {
  it("is empty when AI was not needed or worked", () => {
    expect(aiNotice(scanResult("not_requested", null))).toBeNull();
    expect(aiNotice(scanResult("ok", null))).toBeNull();
  });

  it("explains why AI is missing and that the scan is still valid", () => {
    expect(
      aiNotice(scanResult("disabled", "AI explanations are not configured")),
    ).toBe(
      "AI explanations are not configured. The scan results below are still valid.",
    );
  });

  it("does not double the full stop", () => {
    expect(aiNotice(scanResult("unavailable", "The AI service failed."))).toBe(
      "The AI service failed. The scan results below are still valid.",
    );
  });

  it("has a fallback message", () => {
    expect(aiNotice(scanResult("unavailable", null))).toContain(
      "not available",
    );
  });
});
