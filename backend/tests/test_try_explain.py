from pathlib import Path

from app.models import Explanation, Finding, Severity
from scripts.try_explain import format_finding, main

SAMPLES = Path(__file__).resolve().parents[1] / "samples"


def make_finding(explanation=None):
    return Finding(
        scanner="bandit",
        rule_id="B602",
        title="shell_true",
        message="Shell risk",
        severity=Severity.HIGH,
        confidence=Severity.HIGH,
        line=14,
        end_line=14,
        snippet="subprocess.call(x, shell=True)",
        explanation=explanation,
    )


def test_a_finding_without_an_explanation_is_one_line():
    assert format_finding(make_finding()) == "[HIGH] B602 line 14: shell_true"


def test_a_finding_with_an_explanation_shows_all_parts():
    text = format_finding(
        make_finding(
            Explanation(
                summary="Runs a shell command.",
                risk="Attackers add commands.",
                fix="subprocess.run(['ls'])\nreturn 0",
                false_positive_likely=True,
            )
        )
    )

    assert "What:  Runs a shell command." in text
    assert "Risk:  Attackers add commands." in text
    assert "    subprocess.run(['ls'])\n    return 0" in text
    assert "may be a false alarm" in text


def test_script_asks_for_a_key_when_none_is_set(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    exit_code = main([str(SAMPLES / "vulnerable.py")])

    assert exit_code == 1
    assert "ANTHROPIC_API_KEY" in capsys.readouterr().out


def test_script_rejects_unknown_file_types(capsys):
    assert main(["notes.txt"]) == 2
    assert "Unsupported" in capsys.readouterr().out
