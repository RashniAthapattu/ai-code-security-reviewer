import pytest

from app.main import ai_limiter, scan_limiter


@pytest.fixture(autouse=True)
def fresh_rate_limits():
    """Every test starts with empty rate-limit counters."""
    scan_limiter.reset()
    ai_limiter.reset()
