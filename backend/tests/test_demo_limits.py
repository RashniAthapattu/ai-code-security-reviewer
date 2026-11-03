import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CODE = "import subprocess\nsubprocess.call(cmd, shell=True)\n"


def post(explain=False, code=CODE):
    return client.post("/scan", json={"code": code, "explain": explain})


def test_too_many_scans_get_a_429_with_retry_after(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_HOUR", "2")

    assert [post().status_code for _ in range(3)] == [200, 200, 429]
    blocked = post()
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) > 0
    assert "Too many scans" in blocked.json()["detail"]


def test_zero_turns_the_scan_limit_off(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_HOUR", "0")

    assert all(post().status_code == 200 for _ in range(5))


@pytest.fixture
def ai_calls(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    calls = []

    def fake(code, language, findings, settings):
        calls.append(code)
        return {}

    monkeypatch.setattr("app.main.explain_findings", fake)
    return calls


def test_code_over_the_ai_limit_is_scanned_but_not_sent_to_the_ai(
    monkeypatch, ai_calls
):
    monkeypatch.setenv("AI_MAX_CODE_LENGTH", "10")

    body = post(explain=True).json()

    assert ai_calls == []
    assert len(body["findings"]) > 0
    assert body["ai_status"] == "unavailable"
    assert "too long" in body["ai_message"]


def test_ai_has_its_own_hourly_limit(monkeypatch, ai_calls):
    monkeypatch.setenv("AI_RATE_LIMIT_PER_HOUR", "1")

    first = post(explain=True).json()
    second = post(explain=True).json()
    plain = post(explain=False)

    assert first["ai_status"] == "ok"
    assert second["ai_status"] == "unavailable"
    assert "limit" in second["ai_message"]
    assert len(second["findings"]) > 0
    assert len(ai_calls) == 1
    assert plain.status_code == 200
