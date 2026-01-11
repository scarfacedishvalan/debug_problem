import time
import pytest
from rate_limiter import RateLimiter

@pytest.fixture
def limiter():
    # Use a small window for fast tests
    return RateLimiter(limit=3, window_seconds=2)

def test_allows_up_to_limit(limiter):
    user = 'alice'
    assert limiter.allow_request(user)
    assert limiter.allow_request(user)
    assert limiter.allow_request(user)
    assert not limiter.allow_request(user)

def test_separate_users(limiter):
    assert limiter.allow_request('alice')
    assert limiter.allow_request('bob')
    assert limiter.allow_request('alice')
    assert limiter.allow_request('bob')

def test_window_resets(limiter):
    user = 'alice'
    for _ in range(3):
        assert limiter.allow_request(user)
    assert not limiter.allow_request(user)
    time.sleep(2.1)  # Wait for window to expire
    assert limiter.allow_request(user)

def test_old_requests_are_cleaned(limiter):
    user = 'alice'
    assert limiter.allow_request(user)
    time.sleep(1)
    assert limiter.allow_request(user)
    time.sleep(1.1)
    # The first request should now be out of window
    assert limiter.allow_request(user)
    assert limiter.allow_request(user)  # Should still allow up to limit
    assert not limiter.allow_request(user)

def test_no_timestamps_added_on_reject(limiter):
    user = 'alice'
    for _ in range(3):
        assert limiter.allow_request(user)
    assert not limiter.allow_request(user)
    # Wait for window to expire
    time.sleep(2.1)
    # Should only allow up to limit again
    for _ in range(3):
        assert limiter.allow_request(user)
    assert not limiter.allow_request(user)
