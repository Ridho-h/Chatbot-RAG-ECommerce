"""
Role-based access control (RBAC) dependencies for FastAPI.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import structlog

from app.auth.jwt_handler import verify_token
from app.auth.models import Role, User, user_store

logger = structlog.get_logger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    FastAPI dependency that extracts and validates the current user from JWT.

    Raises:
        HTTPException 401: If token is missing, invalid, or expired.
        HTTPException 401: If user no longer exists.
    """
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = user_store.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def require_role(required_role: Role):
    """
    Factory that creates a FastAPI dependency requiring a specific role.

    Usage:
        @router.get("/admin-only", dependencies=[Depends(require_role(Role.ADMIN))])
        async def admin_endpoint(): ...

    Or in the function signature:
        async def admin_endpoint(user: User = Depends(require_role(Role.ADMIN))): ...
    """

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role != required_role:
            logger.warning(
                "access_denied",
                username=current_user.username,
                required_role=required_role.value,
                user_role=current_user.role.value,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role.value}",
            )
        return current_user

    return role_checker
