import os
from dataclasses import dataclass

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_MAX_EXPLAINED_FINDINGS = 20
DEFAULT_RATE_LIMIT_PER_HOUR = 60
DEFAULT_AI_RATE_LIMIT_PER_HOUR = 10
DEFAULT_AI_MAX_CODE_LENGTH = 20_000
DEFAULT_ALLOWED_ORIGINS = ("http://localhost:3000",)


@dataclass(frozen=True)
class Settings:
    anthropic_model: str
    max_explained_findings: int
    ai_enabled: bool
    allowed_origins: tuple[str, ...] = DEFAULT_ALLOWED_ORIGINS
    rate_limit_per_hour: int = DEFAULT_RATE_LIMIT_PER_HOUR
    ai_rate_limit_per_hour: int = DEFAULT_AI_RATE_LIMIT_PER_HOUR
    ai_max_code_length: int = DEFAULT_AI_MAX_CODE_LENGTH


def get_settings() -> Settings:
    """Read settings from environment variables.

    Read on every call (not cached) so tests and deployments can change them.
    The API key itself is never stored here; the Anthropic client reads it
    from ANTHROPIC_API_KEY.
    """
    return Settings(
        anthropic_model=os.environ.get("ANTHROPIC_MODEL") or DEFAULT_MODEL,
        max_explained_findings=_positive_int(
            os.environ.get("MAX_EXPLAINED_FINDINGS"), DEFAULT_MAX_EXPLAINED_FINDINGS
        ),
        ai_enabled=bool(os.environ.get("ANTHROPIC_API_KEY")),
        allowed_origins=_origins(os.environ.get("ALLOWED_ORIGINS")),
        rate_limit_per_hour=_non_negative_int(
            os.environ.get("RATE_LIMIT_PER_HOUR"), DEFAULT_RATE_LIMIT_PER_HOUR
        ),
        ai_rate_limit_per_hour=_non_negative_int(
            os.environ.get("AI_RATE_LIMIT_PER_HOUR"), DEFAULT_AI_RATE_LIMIT_PER_HOUR
        ),
        ai_max_code_length=_positive_int(
            os.environ.get("AI_MAX_CODE_LENGTH"), DEFAULT_AI_MAX_CODE_LENGTH
        ),
    )


def _positive_int(value: str | None, default: int) -> int:
    try:
        number = int(value) if value else default
    except ValueError:
        return default
    return number if number > 0 else default


def _non_negative_int(value: str | None, default: int) -> int:
    """Like _positive_int, but 0 is allowed (it means "no limit")."""
    try:
        number = int(value) if value else default
    except ValueError:
        return default
    return number if number >= 0 else default


def _origins(value: str | None) -> tuple[str, ...]:
    """Parse a comma-separated list of website addresses allowed to call the API."""
    origins = tuple(
        o.strip().rstrip("/") for o in (value or "").split(",") if o.strip()
    )
    return origins or DEFAULT_ALLOWED_ORIGINS
