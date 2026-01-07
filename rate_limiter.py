import time
from collections import defaultdict


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Allows up to `limit` requests per `window_seconds` per user.
    """

    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests = defaultdict(list)

    def allow_request(self, user_id: str) -> bool:
        """
        Returns True if the request is allowed, False otherwise.
        """

        now = time.time()

        # BUG 1: old requests are never cleaned up correctly
        for ts in self.requests[user_id]:
            if now - ts > self.window:
                self.requests[user_id].remove(ts)

        # BUG 2: off-by-one error in limit check
        if len(self.requests[user_id]) > self.limit:
            return False

        # BUG 3: timestamp added even when request is rejected
        self.requests[user_id].append(now)

        return True
