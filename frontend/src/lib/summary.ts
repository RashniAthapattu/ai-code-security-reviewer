import type { Finding, ScanResult, Severity } from "./types";

export const SEVERITY_ORDER: Severity[] = ["high", "medium", "low"];

/** How many findings there are of each severity. */
export function countBySeverity(findings: Finding[]): Record<Severity, number> {
  const counts: Record<Severity, number> = { high: 0, medium: 0, low: 0 };
  for (const finding of findings) counts[finding.severity] += 1;
  return counts;
}

/** A one-line summary such as "3 findings: 1 high, 2 low". */
export function summaryText(findings: Finding[]): string {
  if (findings.length === 0) return "No problems found.";
  const counts = countBySeverity(findings);
  const parts = SEVERITY_ORDER.filter((s) => counts[s] > 0).map(
    (s) => `${counts[s]} ${s}`,
  );
  const noun = findings.length === 1 ? "finding" : "findings";
  return `${findings.length} ${noun}: ${parts.join(", ")}`;
}

/** Most serious first; findings of the same severity stay in line order. */
export function sortBySeverity(findings: Finding[]): Finding[] {
  const rank = (f: Finding) => SEVERITY_ORDER.indexOf(f.severity);
  return [...findings].sort((a, b) => rank(a) - rank(b) || a.line - b.line);
}

/** A message to show when AI explanations were asked for but are missing. */
export function aiNotice(result: ScanResult): string | null {
  if (result.ai_status !== "disabled" && result.ai_status !== "unavailable") {
    return null;
  }
  const reason = (result.ai_message ?? "AI explanations are not available").replace(
    /\.+$/,
    "",
  );
  return `${reason}. The scan results below are still valid.`;
}
