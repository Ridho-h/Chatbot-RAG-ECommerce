"""
Rate limiting middleware using slowapi.
Limits requests per minute per IP address.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings

# Create the limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
)


def setup_rate_limiter(app):
    """
    Attach the rate limiter to a FastAPI application.

    Args:
        app: The FastAPI application instance.
    """
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please try again later.",
                "retry_after_seconds": 60,
            },
        )
