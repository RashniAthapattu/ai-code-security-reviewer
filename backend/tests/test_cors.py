from fastapi.testclient import TestClient

from app.config import DEFAULT_ALLOWED_ORIGINS, get_settings
from app.main import app

client = TestClient(app)


def preflight(origin: str):
    return client.options(
        "/scan",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_allowed_website_can_call_the_api():
    response = preflight("http://localhost:3000")
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_other_websites_are_not_allowed():
    response = preflight("https://evil.example")
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_default_origin_is_local_website(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    assert get_settings().allowed_origins == DEFAULT_ALLOWED_ORIGINS


def test_origins_can_be_set_by_environment(monkeypatch):
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://a.app/, https://b.app ,")
    assert get_settings().allowed_origins == ("https://a.app", "https://b.app")
