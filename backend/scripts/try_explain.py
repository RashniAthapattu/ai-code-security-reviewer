"""Try the scanner and the AI explanations on a file.

Run from the backend folder:

    python -m scripts.try_explain samples/vulnerable.py

Needs ANTHROPIC_API_KEY to be set. The file is only read, never executed.
"""

import argparse
import sys
from pathlib import Path

from app.config import get_settings
from app.explainer import ExplanationError, explain_findings
from app.models import Finding
from app.scanners import ScannerError, scan_code

LANGUAGES = {".py": "python", ".js": "javascript", ".ts": "typescript"}


def format_finding(finding: Finding) -> str:
    severity = finding.severity.value.upper()
    header = f"[{severity}] {finding.rule_id} line {finding.line}: {finding.title}"
    lines = [header]
    if finding.explanation:
        explanation = finding.explanation
        lines.append(f"  What:  {explanation.summary}")
        lines.append(f"  Risk:  {explanation.risk}")
        lines.append("  Fix:")
        lines.extend(f"    {line}" for line in explanation.fix.splitlines())
        if explanation.false_positive_likely:
            lines.append("  Note:  the AI thinks this may be a false alarm")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path, help="a .py, .js or .ts file")
    args = parser.parse_args(argv)

    language = LANGUAGES.get(args.path.suffix)
    if language is None:
        print(f"Unsupported file type: {args.path.suffix or 'none'}")
        return 2

    settings = get_settings()
    if not settings.ai_enabled:
        print("Set ANTHROPIC_API_KEY first, for example:")
        print("  export ANTHROPIC_API_KEY=your-key-here")
        return 1

    code = args.path.read_text(encoding="utf-8")
    try:
        result = scan_code(code, language)
    except ScannerError as exc:
        print(f"Scan failed: {exc}")
        return 1

    print(f"{args.path}: {len(result.findings)} finding(s)")
    if result.findings:
        print(f"Asking {settings.anthropic_model} to explain them...\n")
        try:
            explanations = explain_findings(code, language, result.findings, settings)
        except ExplanationError as exc:
            print(f"AI explanations failed: {exc}")
            return 1
        for index, explanation in explanations.items():
            result.findings[index].explanation = explanation

    for finding in result.findings:
        print(format_finding(finding), end="\n\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
