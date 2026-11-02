from fastapi.testclient import TestClient

from app.main import app
from app.models import MAX_CODE_LENGTH
from app.scanners.bandit_scanner import ScannerError

client = TestClient(app)

VULNERABLE_CODE = "import subprocess\nsubprocess.call(cmd, shell=True)\n"


def test_scan_returns_findings():
    response = client.post("/scan", json={"code": VULNERABLE_CODE})

    assert response.status_code == 200
    body = response.json()
    assert body["errors"] == []
    finding = next(f for f in body["findings"] if f["rule_id"] == "B602")
    assert finding["severity"] == "high"
    assert finding["line"] == 2


def test_scan_javascript_uses_semgrep():
    response = client.post(
        "/scan", json={"code": "eval(userInput);\n", "language": "javascript"}
    )

    assert response.status_code == 200
    findings = response.json()["findings"]
    assert [(f["scanner"], f["rule_id"]) for f in findings] == [("semgrep", "js-eval")]


def test_scan_of_clean_code_returns_no_findings():
    response = client.post("/scan", json={"code": "print('hello')\n"})

    assert response.status_code == 200
    assert response.json()["findings"] == []


def test_empty_code_is_rejected():
    response = client.post("/scan", json={"code": ""})

    assert response.status_code == 422


def test_code_over_the_size_limit_is_rejected():
    response = client.post("/scan", json={"code": "x" * (MAX_CODE_LENGTH + 1)})

    assert response.status_code == 422


def test_unsupported_language_is_rejected():
    response = client.post("/scan", json={"code": "puts 1", "language": "ruby"})

    assert response.status_code == 422


def test_scanner_failure_returns_503(monkeypatch):
    def broken_scan(code, language):
        raise ScannerError("Bandit took too long and was stopped")

    monkeypatch.setattr("app.main.scan_code", broken_scan)

    response = client.post("/scan", json={"code": "print(1)"})

    assert response.status_code == 503
    assert "too long" in response.json()["detail"]
