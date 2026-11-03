import type { Finding, Severity } from "@/lib/types";

const BADGE: Record<Severity, string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  medium: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
  low: "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300",
};

const BORDER: Record<Severity, string> = {
  high: "border-l-red-500",
  medium: "border-l-amber-500",
  low: "border-l-blue-500",
};

// Only link to web pages, whatever the scanner returned.
function safeLink(url: string | null): string | null {
  return url && url.startsWith("https://") ? url : null;
}

export default function FindingCard({ finding }: { finding: Finding }) {
  const link = safeLink(finding.more_info);
  const lines =
    finding.end_line > finding.line
      ? `Lines ${finding.line}-${finding.end_line}`
      : `Line ${finding.line}`;

  return (
    <article
      className={`rounded-lg border border-l-4 border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900 ${BORDER[finding.severity]}`}
    >
      <header className="flex flex-wrap items-center gap-2">
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${BADGE[finding.severity]}`}
        >
          {finding.severity}
        </span>
        <h3 className="font-medium">{finding.title}</h3>
      </header>

      <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
        {lines} · {finding.rule_id} · {finding.scanner}
        {finding.cwe !== null && ` · CWE-${finding.cwe}`}
      </p>

      <p className="mt-3 text-sm">{finding.message}</p>

      {/* Shown as plain text, never as HTML. */}
      <pre className="mt-3 overflow-x-auto rounded-md bg-zinc-100 p-3 font-mono text-xs dark:bg-zinc-950">
        {finding.snippet}
      </pre>

      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-block text-sm underline"
        >
          Learn more
        </a>
      )}
    </article>
  );
}
