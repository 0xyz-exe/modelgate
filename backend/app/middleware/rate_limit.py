"""Rate limiting middleware"""
from fastapi import Header, HTTPException
from app.services.rate_limit import rate_limiter


async def check_rate_limit(
    authorization: str = Header(...),
    x_rate_limit: int = 60  # Default: 60 requests per minute
):
    """Check rate limit for API key"""
    # Extract key from Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization[7:]
    
    # Check rate limit (using token hash as key)
    allowed, info = rate_limiter.check_limit(
        key=f"ratelimit:{token[:16]}",  # Use prefix as key
        limit=x_rate_limit,
        window_seconds=60
    )
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": {
                    "type": "rate_limit_error",
                    "code": "rate_limit_exceeded",
                    "message": f"Rate limit exceeded: {x_rate_limit} requests per minute"
                }
            },
            headers={
                "X-RateLimit-Limit": str(info["limit"]),
                "X-RateLimit-Remaining": str(info["remaining"]),
                "X-RateLimit-Reset": str(info["reset"]),
                "Retry-After": "60"
            }
        )
    
    return info
