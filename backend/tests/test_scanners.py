from app.scanners import scan_code

PYTHON_CODE = "import hashlib\nhashlib.md5(b'x')\neval(input())\n"
JS_CODE = 'const apiKey = "abc123";\neval(input);\n'


def test_python_is_scanned_with_bandit():
    result = scan_code(PYTHON_CODE, "python")

    assert {finding.scanner for finding in result.findings} == {"bandit"}


def test_javascript_is_scanned_with_semgrep():
    result = scan_code(JS_CODE, "javascript")

    assert {finding.scanner for finding in result.findings} == {"semgrep"}


def test_typescript_is_scanned_with_semgrep():
    result = scan_code(JS_CODE, "typescript")

    assert {finding.scanner for finding in result.findings} == {"semgrep"}


def test_findings_are_sorted_by_line():
    result = scan_code(PYTHON_CODE, "python")
    lines = [finding.line for finding in result.findings]

    assert lines == sorted(lines)
    assert len(lines) >= 2
