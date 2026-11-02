import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from app.models import Finding, ScanResult, Severity
from app.scanners.bandit_scanner import ScannerError

SCAN_TIMEOUT_SECONDS = 60
RULES_DIR = Path(__file__).resolve().parents[2] / "rules" / "semgrep"

# File extension Semgrep uses to pick the language for submitted code
EXTENSIONS = {"javascript": ".js", "typescript": ".ts"}

# Semgrep's own severity names mapped to ours
SEVERITIES = {"ERROR": Severity.HIGH, "WARNING": Severity.MEDIUM, "INFO": Severity.LOW}


def scan_with_semgrep(code: str, language: str) -> ScanResult:
    """Scan source code with Semgrep, using the rules stored in this repository.

    The code is written to a temporary file and analysed statically.
    It is never imported or executed. Only local rules are used, so scans
    work offline and give the same results every time.
    """
    if language not in EXTENSIONS:
        raise ValueError(f"Semgrep scanning does not support '{language}'")

    with tempfile.TemporaryDirectory() as tmp_dir:
        source = Path(tmp_dir) / f"submitted{EXTENSIONS[language]}"
        source.write_text(code, encoding="utf-8")

        command = [
            _semgrep_executable(),
            "--config",
            str(RULES_DIR),
            "--json",
            "--quiet",
            "--metrics=off",
            "--disable-version-check",
            str(source),
        ]
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=SCAN_TIMEOUT_SECONDS,
                check=False,
                env={**os.environ, "SEMGREP_SEND_METRICS": "off"},
            )
        except subprocess.TimeoutExpired as exc:
            raise ScannerError("Semgrep took too long and was stopped") from exc

    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ScannerError(f"Semgrep returned unreadable output: {exc}") from exc

    lines = code.splitlines()
    findings = _unique(_to_finding(item, lines) for item in report.get("results", []))
    errors = [
        item.get("message") or item.get("long_msg") or "unknown error"
        for item in report.get("errors", [])
    ]
    return ScanResult(findings=findings, errors=errors)


def _semgrep_executable() -> str:
    found = shutil.which("semgrep")
    if found:
        return found
    # Fall back to the virtual environment this program is running from
    return str(Path(sys.executable).parent / "semgrep")


def _to_finding(item: dict, lines: list[str]) -> Finding:
    extra = item["extra"]
    metadata = extra.get("metadata", {})
    start_line = item["start"]["line"]
    end_line = item["end"]["line"]
    references = metadata.get("references") or []
    rule_id = item["check_id"].rsplit(".", 1)[-1]
    return Finding(
        scanner="semgrep",
        rule_id=rule_id,
        title=metadata.get("title", rule_id),
        message=" ".join(extra["message"].split()),
        severity=SEVERITIES.get(extra.get("severity", ""), Severity.MEDIUM),
        confidence=Severity(metadata.get("confidence", "MEDIUM").lower()),
        line=start_line,
        end_line=end_line,
        # Semgrep does not return the matched code without a login, so read it
        # from the submitted source instead
        snippet="\n".join(lines[start_line - 1 : end_line]),
        cwe=_cwe_number(metadata.get("cwe")),
        more_info=references[0] if references else None,
    )


def _cwe_number(cwe) -> int | None:
    if isinstance(cwe, list):
        cwe = cwe[0] if cwe else None
    match = re.search(r"CWE-(\d+)", cwe or "")
    return int(match.group(1)) if match else None


def _unique(findings):
    """Drop repeated reports of the same rule on the same lines."""
    seen = set()
    unique = []
    for finding in findings:
        key = (finding.rule_id, finding.line, finding.end_line)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
    return unique
