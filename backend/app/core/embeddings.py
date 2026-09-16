"""
Embedding model loader — initializes HuggingFace embeddings for local inference.
"""

import structlog
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import settings

logger = structlog.get_logger(__name__)

_embeddings_instance: HuggingFaceEmbeddings | None = None


def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Get or create the singleton embedding model instance.
    Uses HuggingFace sentence-transformers for free, local inference.
    """
    global _embeddings_instance

    if _embeddings_instance is None:
        logger.info(
            "loading_embeddings",
            model=settings.EMBEDDING_MODEL_NAME,
        )
        _embeddings_instance = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
        logger.info("embeddings_loaded", model=settings.EMBEDDING_MODEL_NAME)

    return _embeddings_instance
