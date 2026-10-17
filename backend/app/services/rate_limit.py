"""Rate limiting service"""
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
import threading


class RateLimiter:
    """In-memory rate limiter with fixed window"""
    
    def __init__(self):
        self._counters = defaultdict(lambda: {"count": 0, "reset_at": None})
        self._lock = threading.Lock()
    
    def check_limit(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int = 60
    ) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        
        Returns:
            (allowed: bool, info: dict)
        """
        with self._lock:
            now = datetime.utcnow()
            counter = self._counters[key]
            
            # Reset if window expired
            if counter["reset_at"] is None or now >= counter["reset_at"]:
                counter["count"] = 0
                counter["reset_at"] = now + timedelta(seconds=window_seconds)
            
            # Check limit
            if counter["count"] >= limit:
                return False, {
                    "limit": limit,
                    "remaining": 0,
                    "reset": int(counter["reset_at"].timestamp())
                }
            
            # Increment counter
            counter["count"] += 1
            
            return True, {
                "limit": limit,
                "remaining": limit - counter["count"],
                "reset": int(counter["reset_at"].timestamp())
            }
    
    def reset(self, key: str):
        """Reset counter for a key"""
        with self._lock:
            if key in self._counters:
                del self._counters[key]


# Global rate limiter instance
rate_limiter = RateLimiter()
