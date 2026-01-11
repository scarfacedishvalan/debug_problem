import time
from collections import defaultdict


class RateLimiter:
    """
    Fixed-window rate limiter using counters.
    Allows up to `limit` requests per window per user.
    NOTE: This is approximate and may allow bursts at window boundaries.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        # user_id -> (window_id, count)
        self.counters = defaultdict(lambda: (0, 0))

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        window_id = int(now // self.window)

        last_window_id, count = self.counters[user_id]

        if window_id != last_window_id:
            # New window → reset counter
            self.counters[user_id] = (window_id, 1)
            return True

        # Same window
        if count >= self.limit:
            return False

        self.counters[user_id] = (window_id, count + 1)
        return True
