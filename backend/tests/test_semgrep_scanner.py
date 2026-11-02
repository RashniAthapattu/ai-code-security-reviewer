import pytest

from app.models import Severity
from app.scanners.semgrep_scanner import scan_with_semgrep

VULNERABLE_JS = """\
const crypto = require("crypto");
const child_process = require("child_process");
const apiKey = "sk_live_123456";

function handle(input) {
  eval(input);
  document.getElementById("out").innerHTML = input;
  child_process.exec("ls " + input);
  db.query("SELECT * FROM users WHERE id = " + input);
  https.get(url, { rejectUnauthorized: false });
  return crypto.createHash("md5").update(input).digest("hex");
}
"""

SAFE_JS = """\
const name = "world";

function greet() {
  document.getElementById("out").textContent = name;
  child_process.exec("ls -la");
  db.query("SELECT * FROM users WHERE id = $1", [id]);
  return crypto.createHash("sha256");
}
"""


def findings_by_rule(result):
    return {finding.rule_id: finding for finding in result.findings}


def test_finds_known_javascript_vulnerabilities():
    result = scan_with_semgrep(VULNERABLE_JS, "javascript")

    assert set(findings_by_rule(result)) == {
        "js-hardcoded-secret",
        "js-eval",
        "js-innerhtml-assignment",
        "js-child-process-exec",
        "js-sql-string-building",
        "js-tls-verification-disabled",
        "js-weak-hash",
    }
    assert result.errors == []


def test_finding_details_are_filled_in():
    result = scan_with_semgrep(VULNERABLE_JS, "javascript")
    eval_finding = findings_by_rule(result)["js-eval"]

    assert eval_finding.scanner == "semgrep"
    assert eval_finding.title == "Use of eval"
    assert eval_finding.severity == Severity.HIGH
    assert eval_finding.confidence == Severity.HIGH
    assert eval_finding.line == 6
    assert eval_finding.snippet == "  eval(input);"
    assert eval_finding.cwe == 95
    assert eval_finding.more_info.startswith("https://")


def test_safe_code_has_no_findings():
    result = scan_with_semgrep(SAFE_JS, "javascript")

    assert result.findings == []


def test_typescript_is_scanned_too():
    result = scan_with_semgrep("const run = (s: string) => eval(s);\n", "typescript")

    assert [f.rule_id for f in result.findings] == ["js-eval"]


def test_secret_rule_reports_each_line_once_and_skips_empty_values():
    code = 'const password = "";\nuser.password = "abc123";\nconst token = "t0k3n";\n'

    result = scan_with_semgrep(code, "javascript")

    assert [f.line for f in result.findings] == [2, 3]


def test_unsupported_language_is_rejected():
    with pytest.raises(ValueError):
        scan_with_semgrep("puts 1", "ruby")


def test_submitted_code_is_never_executed(tmp_path):
    marker = tmp_path / "executed.txt"
    code = f"require('fs').writeFileSync({str(marker)!r}, 'boom');\n"

    scan_with_semgrep(code, "javascript")

    assert not marker.exists()
