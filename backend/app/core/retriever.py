"""
Retriever wrapper — wraps the Pinecone retriever with result formatting.
"""

import uuid
import structlog
from langchain_core.documents import Document

from app.core.vectorstore import get_or_build_vectorstore
from app.config import settings

logger = structlog.get_logger(__name__)


def get_retriever():
    """
    Get a configured retriever from the Pinecone vector store.

    Returns:
        A LangChain retriever that returns the top-k most relevant documents.
    """
    vectorstore = get_or_build_vectorstore()
    return vectorstore.as_retriever(
        search_kwargs={"k": settings.RETRIEVER_TOP_K}
    )


def format_retriever_results(docs: list[Document]) -> str:
    """
    Format retrieved documents into a human-readable string for the agent.

    Args:
        docs: List of retrieved Document objects.

    Returns:
        Formatted string containing product information.
    """
    if not docs:
        return "No products found in the database matching your query."

    results = []
    for i, doc in enumerate(docs, 1):
        meta = doc.metadata
        result = (
            f"--- Product {i} ---\n"
            f"Name: {meta.get('product_name', 'N/A')}\n"
            f"Price: {meta.get('discounted_price', 'N/A')}\n"
            f"Rating: {meta.get('rating', 'N/A')} "
            f"({meta.get('rating_count', 'N/A')} reviews)\n"
            f"Link: {meta.get('product_link', 'N/A')}\n"
            f"Details: {doc.page_content[:300]}\n"
        )
        results.append(result)

    return "\n".join(results)


def search_products(query: str) -> str:
    """
    Search the product database and return formatted results.
    This is the function exposed as a tool to the agent.

    Args:
        query: The search query.

    Returns:
        Formatted string of matching products.
    """
    logger.info("product_search", query=query)
    retriever = get_retriever()
    docs = retriever.invoke(query)
    formatted = format_retriever_results(docs)
    logger.info("product_search_complete", query=query, results=len(docs))
    return formatted
