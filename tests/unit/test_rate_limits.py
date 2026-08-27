from app.security.rate_limits import InMemoryRateLimiter


def test_limiter_blocks_after_limit_and_resets_after_window() -> None:
    now = [10.0]
    limiter = InMemoryRateLimiter(clock=lambda: now[0])

    assert limiter.allowed("query:user", limit=2)
    assert limiter.allowed("query:user", limit=2)
    assert not limiter.allowed("query:user", limit=2)

    now[0] += 61
    assert limiter.allowed("query:user", limit=2)
