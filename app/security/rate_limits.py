import time
from collections import defaultdict, deque
from collections.abc import Callable


class InMemoryRateLimiter:
    """Development limiter; production replaces shared state with Redis."""

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self.clock = clock
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allowed(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        now = self.clock()
        requests = self._requests[key]
        while requests and requests[0] <= now - window_seconds:
            requests.popleft()
        if len(requests) >= limit:
            return False
        requests.append(now)
        return True
