import os
from dataclasses import dataclass

DEFAULT_MODEL = "claude-opus-5-5"
DEFAULT_MAX_EXPLAINED_FINDINGS = 20
DEFAULT_ALLOWED_ORIGINS = ("http://localhost:3000",)


@dataclass(frozen=True)
class Settings:
    anthropic_model: str
    max_explained_findings: int
    ai_enabled: bool
    allowed_origins: tuple[str, ...] = DEFAULT_ALLOWED_ORIGINS


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
    )


def _positive_int(value: str | None, default: int) -> int:
    try:
        number = int(value) if value else default
    except ValueError:
        return default
    return number if number > 0 else default


def _origins(value: str | None) -> tuple[str, ...]:
    """Parse a comma-separated list of website addresses allowed to call the API."""
    origins = tuple(
        o.strip().rstrip("/") for o in (value or "").split(",") if o.strip()
    )
    return origins or DEFAULT_ALLOWED_ORIGINS
