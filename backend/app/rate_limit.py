import time
from collections import defaultdict, deque

WINDOW_SECONDS = 3600


class RateLimiter:
    """Allow each visitor a fixed number of requests per hour.

    Kept in memory, so the count is per server process and resets when the
    server restarts. That is enough to stop a single visitor from running up
    the AI bill on a small demo.
    """

    def __init__(self, window: int = WINDOW_SECONDS) -> None:
        self._window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str, limit: int, now: float | None = None) -> bool:
        """Record a request and say whether it is allowed. 0 means no limit."""
        if limit <= 0:
            return True
        now = time.monotonic() if now is None else now
        hits = self._hits[key]
        while hits and hits[0] <= now - self._window:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True

    def retry_after(self, key: str, now: float | None = None) -> int:
        """Seconds until the oldest request for this visitor expires."""
        now = time.monotonic() if now is None else now
        hits = self._hits.get(key)
        if not hits:
            return 0
        return max(1, int(hits[0] + self._window - now) + 1)

    def reset(self) -> None:
        self._hits.clear()
