"""Unit tests for rate limiting"""
import pytest
import time
from app.services.rate_limit import RateLimiter


def test_rate_limiter_allows_within_limit():
    """Test rate limiter allows requests within limit"""
    limiter = RateLimiter()
    
    # First 5 requests should pass
    for i in range(5):
        allowed, info = limiter.check_limit("test_key", limit=5, window_seconds=60)
        assert allowed
        assert info["limit"] == 5
        assert info["remaining"] == 5 - i - 1


def test_rate_limiter_blocks_over_limit():
    """Test rate limiter blocks requests over limit"""
    limiter = RateLimiter()
    
    # Use up the limit
    for _ in range(3):
        allowed, _ = limiter.check_limit("test_key2", limit=3, window_seconds=60)
        assert allowed
    
    # 4th request should fail
    allowed, info = limiter.check_limit("test_key2", limit=3, window_seconds=60)
    assert not allowed
    assert info["remaining"] == 0


def test_rate_limiter_reset():
    """Test rate limiter reset"""
    limiter = RateLimiter()
    
    # Use up limit
    for _ in range(2):
        limiter.check_limit("test_key3", limit=2, window_seconds=60)
    
    # Should be blocked
    allowed, _ = limiter.check_limit("test_key3", limit=2, window_seconds=60)
    assert not allowed
    
    # Reset
    limiter.reset("test_key3")
    
    # Should work again
    allowed, _ = limiter.check_limit("test_key3", limit=2, window_seconds=60)
    assert allowed


def test_rate_limiter_different_keys():
    """Test rate limiter with different keys"""
    limiter = RateLimiter()
    
    # Key 1
    for _ in range(5):
        allowed, _ = limiter.check_limit("key1", limit=5, window_seconds=60)
        assert allowed
    
    # Key 2 should still work
    allowed, _ = limiter.check_limit("key2", limit=5, window_seconds=60)
    assert allowed


def test_rate_limiter_window_expiry():
    """Test rate limiter window expiry"""
    limiter = RateLimiter()
    
    # Use up limit with 1 second window
    for _ in range(2):
        allowed, _ = limiter.check_limit("test_key4", limit=2, window_seconds=1)
        assert allowed
    
    # Should be blocked
    allowed, _ = limiter.check_limit("test_key4", limit=2, window_seconds=1)
    assert not allowed
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should work again
    allowed, _ = limiter.check_limit("test_key4", limit=2, window_seconds=1)
    assert allowed
