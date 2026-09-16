"""
Pydantic models for chat request/response schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ProductSource(BaseModel):
    """A product source referenced in the response."""
    product_name: str
    discounted_price: str
    rating: str
    rating_count: str
    product_link: str


class ChatResponse(BaseModel):
    """Response body from the chat endpoint."""
    response: str = Field(..., description="The chatbot's response")
    session_id: str = Field(..., description="Session ID for follow-up messages")
    sources: list[ProductSource] = Field(default_factory=list, description="Product sources used")
    thinking_time_ms: float = Field(..., description="Response time in milliseconds")


class HealthResponse(BaseModel):
    """Response body for health check endpoints."""
    status: str
    version: str
    uptime_seconds: float


class ReadinessResponse(BaseModel):
    """Response body for readiness check endpoint."""
    status: str
    faiss_loaded: bool
    llm_provider: str
    embedding_model: str
    active_sessions: int
