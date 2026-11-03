from app.rate_limit import RateLimiter


def test_allows_up_to_the_limit_then_blocks():
    limiter = RateLimiter(window=100)

    assert [limiter.allow("a", 2, now=t) for t in (0, 1, 2)] == [True, True, False]


def test_visitors_are_counted_separately():
    limiter = RateLimiter(window=100)
    limiter.allow("a", 1, now=0)

    assert limiter.allow("a", 1, now=1) is False
    assert limiter.allow("b", 1, now=1) is True


def test_allows_again_after_the_window():
    limiter = RateLimiter(window=100)
    limiter.allow("a", 1, now=0)

    assert limiter.allow("a", 1, now=50) is False
    assert limiter.allow("a", 1, now=101) is True


def test_zero_means_no_limit():
    limiter = RateLimiter(window=100)

    assert all(limiter.allow("a", 0, now=0) for _ in range(1000))


def test_retry_after_counts_down_to_the_oldest_request():
    limiter = RateLimiter(window=100)
    limiter.allow("a", 1, now=0)

    assert limiter.retry_after("a", now=40) == 61
    assert limiter.retry_after("nobody", now=40) == 0
