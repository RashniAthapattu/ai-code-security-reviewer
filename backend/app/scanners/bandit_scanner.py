import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.models import Finding, ScanResult, Severity

SCAN_TIMEOUT_SECONDS = 30


class ScannerError(Exception):
    """Raised when the scanner itself fails (not when it finds problems)."""


def scan_python(code: str) -> ScanResult:
    """Scan Python source code with Bandit.

    The code is written to a temporary file and analysed statically.
    It is never imported or executed.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        source = Path(tmp_dir) / "submitted.py"
        source.write_text(code, encoding="utf-8")

        try:
            completed = subprocess.run(
                [sys.executable, "-m", "bandit", "-f", "json", "-q", str(source)],
                capture_output=True,
                text=True,
                timeout=SCAN_TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ScannerError("Bandit took too long and was stopped") from exc

    # Bandit exits with 1 when it finds issues, so only parse the output
    try:
        report = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ScannerError(f"Bandit returned unreadable output: {exc}") from exc

    findings = [_to_finding(item) for item in report.get("results", [])]
    errors = [
        f"{item.get('reason', 'unknown error')}" for item in report.get("errors", [])
    ]
    return ScanResult(findings=findings, errors=errors)


def _to_finding(item: dict) -> Finding:
    cwe = item.get("issue_cwe") or {}
    line_range = item.get("line_range") or [item["line_number"]]
    return Finding(
        scanner="bandit",
        rule_id=item["test_id"],
        title=item["test_name"],
        message=item["issue_text"],
        severity=Severity(item["issue_severity"].lower()),
        confidence=Severity(item["issue_confidence"].lower()),
        line=item["line_number"],
        end_line=max(line_range),
        snippet=item.get("code", "").rstrip(),
        cwe=cwe.get("id"),
        more_info=item.get("more_info"),
    )
