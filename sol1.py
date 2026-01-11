import time
from collections import defaultdict


class RateLimiter:
    """
    Sliding-window rate limiter using list cleanup.
    Allows up to `limit` requests per `window_seconds` per user.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests = defaultdict(list)

    def allow_request(self, user_id: str) -> bool:
        now = time.time()

        # Remove expired timestamps safely
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if now - ts <= self.window
        ]

        # Enforce limit
        if len(self.requests[user_id]) >= self.limit:
            return False

        # Record allowed request
        self.requests[user_id].append(now)
        return True
