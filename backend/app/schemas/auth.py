"""
Pydantic models for authentication request/response schemas.
"""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request body for login."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)


class RegisterRequest(BaseModel):
    """Request body for registration."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=128)


class AuthResponse(BaseModel):
    """Response body for auth endpoints."""
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
