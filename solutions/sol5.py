import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window = window_seconds
        self.requests = defaultdict(list)

    def allow_request(self, user_id: str) -> bool:
        now = time.time()

        # FIX: clean up using list comprehension
        self.requests[user_id] = [
            ts for ts in self.requests[user_id]
            if now - ts <= self.window
        ]

        # Still incorrect: off-by-one
        if len(self.requests[user_id]) > self.limit:
            return False

        # Still incorrect: timestamp always added
        self.requests[user_id].append(now)

        return True
