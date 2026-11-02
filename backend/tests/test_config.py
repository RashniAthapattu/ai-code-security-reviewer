from app.config import DEFAULT_MODEL, get_settings


def clear(monkeypatch):
    for name in ("ANTHROPIC_API_KEY", "ANTHROPIC_MODEL", "MAX_EXPLAINED_FINDINGS"):
        monkeypatch.delenv(name, raising=False)


def test_defaults_without_any_environment(monkeypatch):
    clear(monkeypatch)

    settings = get_settings()

    assert settings.anthropic_model == DEFAULT_MODEL
    assert settings.max_explained_findings == 20
    assert settings.ai_enabled is False


def test_ai_is_enabled_when_a_key_is_present(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    assert get_settings().ai_enabled is True


def test_empty_key_counts_as_not_configured(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")

    assert get_settings().ai_enabled is False


def test_model_and_limit_can_be_overridden(monkeypatch):
    clear(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
    monkeypatch.setenv("MAX_EXPLAINED_FINDINGS", "5")

    settings = get_settings()

    assert settings.anthropic_model == "claude-sonnet-5-5"
    assert settings.max_explained_findings == 5


def test_bad_limits_fall_back_to_the_default(monkeypatch):
    clear(monkeypatch)
    for bad in ("abc", "0", "-3"):
        monkeypatch.setenv("MAX_EXPLAINED_FINDINGS", bad)

        assert get_settings().max_explained_findings == 20
