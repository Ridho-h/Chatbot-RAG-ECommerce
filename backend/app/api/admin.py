"""
Admin-only endpoints — metrics, re-ingestion, and evaluation results.
Requires ADMIN role.
"""

import json
from pathlib import Path

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.auth.models import Role, User
from app.auth.rbac import require_role
from app.config import settings
from app.core.memory import memory_manager

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/metrics")
async def get_metrics(
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Get application metrics (admin only).
    Returns session stats and system information.
    """
    sessions = memory_manager.get_all_sessions_info()

    return {
        "active_sessions": len(sessions),
        "sessions": sessions,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "search_provider": settings.SEARCH_PROVIDER,
        "langsmith_enabled": settings.LANGCHAIN_TRACING_V2,
        "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
    }


@router.post("/ingest")
async def trigger_ingestion(
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Trigger re-ingestion of the product dataset (admin only).
    Downloads from Kaggle and rebuilds the FAISS index.
    """
    from app.core.vectorstore import build_vectorstore, reset_vectorstore
    from app.data.loader import download_dataset

    logger.info("admin_ingest_triggered", user=current_user.username)

    try:
        # Download dataset
        csv_path = download_dataset()

        # Reset and rebuild vectorstore
        reset_vectorstore()
        vectorstore = build_vectorstore(csv_path)

        return {
            "status": "success",
            "message": "Dataset re-ingested and FAISS index rebuilt",
            "total_vectors": vectorstore.index.ntotal,
        }

    except Exception as e:
        logger.error("admin_ingest_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get("/eval")
async def get_evaluation_results(
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Get the latest evaluation results (admin only).
    Results are read from the evaluation output file.
    """
    eval_file = Path("data/evaluation_results.json")

    if not eval_file.exists():
        return {
            "status": "no_results",
            "message": "No evaluation results found. Run: docker exec chatbot-backend python scripts/evaluate.py",
            "results": None,
        }

    try:
        with open(eval_file, "r") as f:
            results = json.load(f)

        return {
            "status": "success",
            "results": results,
        }

    except Exception as e:
        logger.error("admin_eval_read_error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read evaluation results: {str(e)}",
        )


@router.post("/cleanup-sessions")
async def cleanup_sessions(
    current_user: User = Depends(require_role(Role.ADMIN)),
):
    """
    Manually trigger cleanup of expired sessions (admin only).
    """
    removed = memory_manager.cleanup_expired()
    return {
        "status": "success",
        "sessions_removed": removed,
        "active_sessions": memory_manager.get_active_session_count(),
    }
