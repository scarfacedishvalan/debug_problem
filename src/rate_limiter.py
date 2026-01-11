import time
from collections import defaultdict, deque


class RateLimiter:
    """
    Sliding-window rate limiter using deque for efficient cleanup.
    Allows up to `limit` requests per `window_seconds` per user.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests = defaultdict(deque)

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        q = self.requests[user_id]

        # Remove expired timestamps from the front
        while q and now - q[0] > self.window:
            q.popleft()

        # Enforce limit
        if len(q) >= self.limit:
            return False

        # Record allowed request
        q.append(now)
        return True
