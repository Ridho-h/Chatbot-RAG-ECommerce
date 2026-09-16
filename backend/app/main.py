"""
FastAPI application — entry point with lifespan management,
middleware setup, CORS, and router inclusion.
"""

import asyncio
from contextlib import asynccontextmanager
import uuid

import langchain_core.tools.base
langchain_core.tools.base.uuid = uuid

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.auth.models import user_store
from app.core.memory import memory_manager
from app.middleware.logging_middleware import LoggingMiddleware, configure_structlog
from app.middleware.rate_limiter import setup_rate_limiter

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler:
    - Startup: configure logging, seed admin, load vectorstore, start cleanup task
    - Shutdown: graceful cleanup
    """
    # ── Startup ──────────────────────────────────────────────────────────
    configure_structlog()
    logger.info("starting_application", app=settings.APP_NAME, version=settings.APP_VERSION)

    # Seed admin user
    admin = user_store.seed_admin(settings.ADMIN_USERNAME, settings.ADMIN_PASSWORD)
    logger.info("admin_seeded", username=admin.username)

    # Load or build vector store (in background to not block startup)
    logger.info("initializing_vectorstore")
    try:
        from app.core.vectorstore import get_or_build_vectorstore
        get_or_build_vectorstore()
        logger.info("vectorstore_ready")
    except Exception as e:
        logger.error("vectorstore_init_failed", error=str(e))
        logger.warning("app_starting_without_vectorstore", msg="Run ingestion to fix.")

    # Start periodic session cleanup
    cleanup_task = asyncio.create_task(_periodic_session_cleanup())

    logger.info("application_started", app=settings.APP_NAME)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    logger.info("shutting_down")
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    logger.info("shutdown_complete")


async def _periodic_session_cleanup():
    """Periodically clean up expired sessions (every 5 minutes)."""
    while True:
        await asyncio.sleep(300)  # 5 minutes
        try:
            removed = memory_manager.cleanup_expired()
            if removed > 0:
                logger.info("session_cleanup", removed=removed)
        except Exception as e:
            logger.error("session_cleanup_error", error=str(e))


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade E-Commerce RAG Chatbot with RBAC, tracing, and evaluation",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Middleware (order matters: last added = first executed) ───────────
    app.add_middleware(LoggingMiddleware)
    setup_rate_limiter(app)

    # ── Routes ───────────────────────────────────────────────────────────
    app.include_router(api_router)

    return app


# Create the app instance (used by uvicorn)
app = create_app()
