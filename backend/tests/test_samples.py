from pathlib import Path

from app.scanners import scan_code

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def test_python_sample_triggers_the_expected_rules():
    result = scan_code((SAMPLES / "vulnerable.py").read_text(), "python")
    rules = {finding.rule_id for finding in result.findings}

    # shell=True, hard-coded password, MD5, pickle, eval
    assert {"B602", "B105", "B324", "B301", "B307"} <= rules


def test_javascript_sample_triggers_the_expected_rules():
    result = scan_code((SAMPLES / "vulnerable.js").read_text(), "javascript")
    rules = {finding.rule_id for finding in result.findings}

    assert rules == {
        "js-hardcoded-secret",
        "js-innerhtml-assignment",
        "js-child-process-exec",
        "js-sql-string-building",
        "js-eval",
        "js-weak-hash",
    }
