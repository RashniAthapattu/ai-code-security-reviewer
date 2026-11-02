import pytest

from app.models import Severity
from app.scanners.bandit_scanner import scan_python

VULNERABLE_CODE = """\
import subprocess
import hashlib


def run(command):
    return subprocess.call(command, shell=True)


def fingerprint(data):
    return hashlib.md5(data).hexdigest()


password = "hunter2"
"""

CLEAN_CODE = """\
def add(a: int, b: int) -> int:
    return a + b
"""


def rule_ids(result):
    return {finding.rule_id for finding in result.findings}


def test_finds_known_vulnerabilities():
    result = scan_python(VULNERABLE_CODE)

    # B602: shell=True, B324: weak MD5 hash, B105: hardcoded password
    assert {"B602", "B324", "B105"} <= rule_ids(result)


def test_finding_details_are_filled_in():
    result = scan_python(VULNERABLE_CODE)
    shell_finding = next(f for f in result.findings if f.rule_id == "B602")

    assert shell_finding.scanner == "bandit"
    assert shell_finding.severity == Severity.HIGH
    assert shell_finding.line == 6
    assert "shell=True" in shell_finding.snippet
    assert shell_finding.cwe == 78
    assert shell_finding.more_info.startswith("https://")


def test_clean_code_has_no_findings():
    result = scan_python(CLEAN_CODE)

    assert result.findings == []
    assert result.errors == []


def test_syntax_errors_are_reported_not_raised():
    result = scan_python("def broken(:\n    pass\n")

    assert result.findings == []
    assert result.errors


def test_submitted_code_is_never_executed(tmp_path):
    marker = tmp_path / "executed.txt"
    code = f"open({str(marker)!r}, 'w').write('boom')\n"

    scan_python(code)

    assert not marker.exists()


@pytest.mark.parametrize("code", ["", "\n\n"])
def test_empty_code_is_fine(code):
    result = scan_python(code)

    assert result.findings == []
