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


def test_demo_limits_have_safe_defaults(monkeypatch):
    for name in ("RATE_LIMIT_PER_HOUR", "AI_RATE_LIMIT_PER_HOUR", "AI_MAX_CODE_LENGTH"):
        monkeypatch.delenv(name, raising=False)

    settings = get_settings()

    assert settings.rate_limit_per_hour == 60
    assert settings.ai_rate_limit_per_hour == 10
    assert settings.ai_max_code_length == 20_000


def test_demo_limits_can_be_set_and_zero_means_no_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_HOUR", "0")
    monkeypatch.setenv("AI_RATE_LIMIT_PER_HOUR", "5")
    monkeypatch.setenv("AI_MAX_CODE_LENGTH", "1000")

    settings = get_settings()

    assert settings.rate_limit_per_hour == 0
    assert settings.ai_rate_limit_per_hour == 5
    assert settings.ai_max_code_length == 1000


def test_bad_limit_values_fall_back_to_defaults(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_HOUR", "-3")
    monkeypatch.setenv("AI_RATE_LIMIT_PER_HOUR", "lots")
    monkeypatch.setenv("AI_MAX_CODE_LENGTH", "0")

    settings = get_settings()

    assert settings.rate_limit_per_hour == 60
    assert settings.ai_rate_limit_per_hour == 10
    assert settings.ai_max_code_length == 20_000
