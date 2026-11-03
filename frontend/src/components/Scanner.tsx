"use client";

import { useState } from "react";

import FindingCard from "@/components/FindingCard";
import { ScanError, scanCode } from "@/lib/api";
import { aiNotice, sortBySeverity, summaryText } from "@/lib/summary";
import type { Language, ScanResult } from "@/lib/types";

const LANGUAGES: { value: Language; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
];

export default function Scanner() {
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState<Language>("python");
  const [explain, setExplain] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ScanResult | null>(null);

  async function handleScan() {
    setLoading(true);
    setError(null);
    try {
      setResult(await scanCode({ code, language, explain }));
    } catch (err) {
      setResult(null);
      setError(
        err instanceof ScanError ? err.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <label className="block">
        <span className="sr-only">Code to scan</span>
        <textarea
          value={code}
          onChange={(event) => setCode(event.target.value)}
          placeholder="Paste your code here"
          spellCheck={false}
          rows={14}
          className="w-full rounded-lg border border-zinc-300 bg-white p-3 font-mono text-sm dark:border-zinc-700 dark:bg-zinc-900"
        />
      </label>

      <div className="flex flex-wrap items-center gap-4">
        <label className="flex items-center gap-2 text-sm">
          Language
          <select
            value={language}
            onChange={(event) => setLanguage(event.target.value as Language)}
            className="rounded-md border border-zinc-300 bg-white px-2 py-1 dark:border-zinc-700 dark:bg-zinc-900"
          >
            {LANGUAGES.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={explain}
            onChange={(event) => setExplain(event.target.checked)}
          />
          Explain with AI
        </label>

        <button
          type="button"
          onClick={handleScan}
          disabled={loading || code.trim() === ""}
          className="ml-auto rounded-md bg-zinc-900 px-5 py-2 text-sm font-medium text-white hover:bg-zinc-700 disabled:opacity-50 dark:bg-zinc-100 dark:text-zinc-900 dark:hover:bg-zinc-300"
        >
          {loading ? "Scanning..." : "Scan"}
        </button>
      </div>

      {error && (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      )}

      {result && (
        <div className="space-y-3 pt-2">
          <p aria-live="polite" className="font-medium">
            {summaryText(result.findings)}
          </p>
          {aiNotice(result) && (
            <p
              role="status"
              className="rounded-md border border-amber-300 bg-amber-50 p-3 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-200"
            >
              {aiNotice(result)}
            </p>
          )}
          {sortBySeverity(result.findings).map((finding, index) => (
            <FindingCard
              key={`${finding.rule_id}-${finding.line}-${index}`}
              finding={finding}
            />
          ))}
        </div>
      )}
    </section>
  );
}
