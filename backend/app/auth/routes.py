"""
Authentication routes — login and register endpoints.
"""

from fastapi import APIRouter, HTTPException, status
import structlog

from app.auth.models import Role, user_store
from app.auth.jwt_handler import create_access_token
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    AuthResponse,
)

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user account.
    New users are always assigned the CUSTOMER role.
    """
    try:
        user = user_store.create_user(
            username=request.username,
            password=request.password,
            role=Role.CUSTOMER,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )

    logger.info("user_registered", username=user.username, role=user.role.value)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role=user.role.value,
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user and return a JWT token.
    """
    user = user_store.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )

    logger.info("user_login", username=user.username, role=user.role.value)

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        username=user.username,
        role=user.role.value,
    )
