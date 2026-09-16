"""
Dependency injection for FastAPI — provides singleton instances to endpoints.
"""

from app.core.vectorstore import get_or_build_vectorstore
from app.core.memory import memory_manager


def get_vectorstore():
    """Get the singleton Pinecone vector store."""
    return get_or_build_vectorstore()


def get_memory_manager():
    """Get the singleton session memory manager."""
    return memory_manager
