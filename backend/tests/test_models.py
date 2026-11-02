from app.models import Explanation, Finding, ScanRequest, ScanResult, Severity


def make_finding(**overrides):
    values = {
        "scanner": "bandit",
        "rule_id": "B602",
        "title": "subprocess_popen_with_shell_equals_true",
        "message": "Shell injection risk",
        "severity": Severity.HIGH,
        "confidence": Severity.HIGH,
        "line": 3,
        "end_line": 3,
        "snippet": "subprocess.call(cmd, shell=True)",
    }
    return Finding(**{**values, **overrides})


def test_explanations_are_not_requested_by_default():
    assert ScanRequest(code="x = 1").explain is False


def test_scan_result_defaults_to_no_ai():
    result = ScanResult()

    assert result.ai_status == "not_requested"
    assert result.ai_message is None


def test_finding_has_no_explanation_until_one_is_added():
    finding = make_finding()
    assert finding.explanation is None

    finding.explanation = Explanation(
        summary="Runs a shell command built from input.",
        risk="An attacker can append their own commands.",
        fix="subprocess.run(['ls', path], check=True)",
        false_positive_likely=False,
    )

    assert finding.model_dump()["explanation"]["false_positive_likely"] is False
