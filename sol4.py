import time
from collections import defaultdict


class RateLimiter:
    """
    Token bucket rate limiter.
    Tokens refill continuously over time.
    Each request consumes one token.
    """

    def __init__(self, limit: int, window_seconds: int):
        # Capacity = max burst size
        self.capacity = limit

        # Tokens added per second
        self.refill_rate = limit / window_seconds

        # user_id -> (tokens, last_refill_timestamp)
        self.buckets = defaultdict(lambda: (self.capacity, time.time()))

    def allow_request(self, user_id: str) -> bool:
        now = time.time()
        tokens, last_ts = self.buckets[user_id]

        # Refill tokens based on elapsed time
        elapsed = now - last_ts
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)

        if tokens < 1.0:
            # Not enough tokens → reject
            self.buckets[user_id] = (tokens, now)
            return False

        # Consume one token
        tokens -= 1.0
        self.buckets[user_id] = (tokens, now)
        return True
