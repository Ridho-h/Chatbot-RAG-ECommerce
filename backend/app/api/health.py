"""
Health check endpoints — liveness and readiness probes.
"""

import time

from fastapi import APIRouter

from app.config import settings
from app.schemas.chat import HealthResponse, ReadinessResponse

router = APIRouter(tags=["Health"])

_start_time = time.time()


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    Liveness probe — returns 200 if the server is running.
    No auth required.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - _start_time, 2),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness():
    """
    Readiness probe — checks if all critical components are initialized.
    No auth required.
    """
    from app.core.vectorstore import _vectorstore_instance
    from app.core.memory import memory_manager

    faiss_loaded = _vectorstore_instance is not None

    return ReadinessResponse(
        status="ready" if faiss_loaded else "initializing",
        faiss_loaded=faiss_loaded,
        llm_provider=settings.LLM_PROVIDER,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        active_sessions=memory_manager.get_active_session_count(),
    )
