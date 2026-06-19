from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Use memory-backed rate limiting (per IP address)
limiter = Limiter(key_func=get_remote_address)

# Per-user rate limit for authenticated routes (uses current_user.id)
def get_user_id(request):
    """Custom key function for per-user rate limiting."""
    from fastapi import Request
    # Try to get user from request state (set by auth dependency)
    user = getattr(request.state, "user", None)
    if user:
        return f"user:{user.id}"
    return get_remote_address(request)

user_limiter = Limiter(key_func=get_user_id)
