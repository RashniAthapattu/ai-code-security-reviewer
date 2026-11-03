from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.explainer import ExplanationError
from app.main import app
from app.models import Explanation

client = TestClient(app)

VULNERABLE = (
    "import subprocess\nsubprocess.call(cmd, shell=True)\npassword = 'hunter2'\n"
)
CLEAN = "print('hello')\n"


def explanation(text="Explained."):
    return Explanation(
        summary=text,
        risk="Risky.",
        fix="safer()",
        false_positive_likely=False,
    )


def scan(code=VULNERABLE, explain=True):
    response = client.post("/scan", json={"code": code, "explain": explain})
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def ai_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")


@pytest.fixture
def no_ai_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


@pytest.fixture
def explainer(monkeypatch):
    """Replace the real AI call and record how it was used."""
    calls = []
    behaviour = {"result": {}, "error": None}

    def fake_explain_findings(code, language, findings, settings):
        calls.append({"code": code, "language": language, "findings": findings})
        if behaviour["error"]:
            raise behaviour["error"]
        return behaviour["result"]

    monkeypatch.setattr("app.main.explain_findings", fake_explain_findings)
    return SimpleNamespace(calls=calls, behaviour=behaviour)


def test_ai_is_not_used_unless_asked_for(ai_key, explainer):
    body = scan(explain=False)

    assert body["ai_status"] == "not_requested"
    assert explainer.calls == []
    assert all(f["explanation"] is None for f in body["findings"])


def test_explanations_are_added_to_the_right_findings(ai_key, explainer):
    explainer.behaviour["result"] = {1: explanation("Second finding.")}

    body = scan()

    assert body["ai_status"] == "ok"
    assert body["ai_message"] is None
    assert body["findings"][0]["explanation"] is None
    assert body["findings"][1]["explanation"]["summary"] == "Second finding."
    assert len(explainer.calls) == 1
    assert explainer.calls[0]["language"] == "python"


def test_scan_still_works_when_no_api_key_is_configured(no_ai_key, explainer):
    body = scan()

    assert body["ai_status"] == "disabled"
    assert "not configured" in body["ai_message"]
    assert len(body["findings"]) >= 2
    assert explainer.calls == []


def test_ai_failure_does_not_fail_the_scan(ai_key, explainer):
    explainer.behaviour["error"] = ExplanationError("The AI service is unavailable")

    body = scan()

    assert body["ai_status"] == "unavailable"
    assert body["ai_message"] == "The AI service is unavailable"
    assert len(body["findings"]) >= 2
    assert all(f["explanation"] is None for f in body["findings"])


def test_clean_code_needs_no_ai_call(ai_key, explainer):
    body = scan(CLEAN)

    assert body["ai_status"] == "ok"
    assert body["findings"] == []
    assert explainer.calls == []
