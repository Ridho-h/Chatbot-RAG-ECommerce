"""
Pinecone vector store management — build from CSV and connect to Pinecone.
"""

import os
import structlog
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config import settings
from app.core.embeddings import get_embeddings
from app.data.loader import load_documents

logger = structlog.get_logger(__name__)

_vectorstore_instance: PineconeVectorStore | None = None


def build_vectorstore(csv_path: str | None = None) -> PineconeVectorStore:
    """
    Build a Pinecone vector store from the product CSV dataset.

    Steps:
        1. Load and clean the CSV into LangChain Documents
        2. Split documents into chunks
        3. Upload documents to Pinecone index

    Args:
        csv_path: Path to the CSV file. Defaults to settings.CSV_FILE_PATH.

    Returns:
        The connected PineconeVectorStore.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    if not settings.PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is missing. Cannot build vector store.")

    csv_path = csv_path or settings.CSV_FILE_PATH
    logger.info("building_vectorstore", csv_path=csv_path, provider="pinecone")

    # Load documents from CSV
    docs = load_documents(csv_path)
    logger.info("documents_loaded", count=len(docs))

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )
    splits = text_splitter.split_documents(docs)
    logger.info("documents_split", chunks=len(splits))

    # Initialize Pinecone
    os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    
    # Optional: ensure index exists (usually handled via UI as per instructions, but good for safety)
    if settings.PINECONE_INDEX_NAME not in pc.list_indexes().names():
        logger.warning(f"Index {settings.PINECONE_INDEX_NAME} not found. Creating it now...")
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=384,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

    # Create embeddings and upload to Pinecone
    embeddings = get_embeddings()
    logger.info("uploading_to_pinecone", index_name=settings.PINECONE_INDEX_NAME)
    
    vectorstore = PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=settings.PINECONE_INDEX_NAME
    )
    logger.info("vectorstore_built", provider="pinecone")

    return vectorstore


def load_vectorstore() -> PineconeVectorStore:
    """
    Connect to a previously built Pinecone vector store.
    """
    if not settings.PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is missing. Cannot connect to vector store.")

    os.environ["PINECONE_API_KEY"] = settings.PINECONE_API_KEY
    logger.info("loading_vectorstore", index_name=settings.PINECONE_INDEX_NAME, provider="pinecone")
    
    embeddings = get_embeddings()
    vectorstore = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings
    )
    logger.info("vectorstore_loaded", provider="pinecone")
    return vectorstore


def get_or_build_vectorstore() -> PineconeVectorStore:
    """
    Get the vector store — connect to Pinecone. 
    Note: Pinecone is cloud-hosted, so 'building' should be triggered manually via script,
    but we fallback to building if needed (though it takes time).
    Uses a module-level singleton to avoid reloading on every request.
    """
    global _vectorstore_instance

    if _vectorstore_instance is not None:
        return _vectorstore_instance

    _vectorstore_instance = load_vectorstore()
    return _vectorstore_instance


def reset_vectorstore() -> None:
    """Reset the singleton instance (used when re-ingesting data)."""
    global _vectorstore_instance
    _vectorstore_instance = None
