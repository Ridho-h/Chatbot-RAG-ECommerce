"""
Tool definitions for the ReAct agent:
  1. Product Database Search — FAISS-based semantic search
  2. Web Search — DuckDuckGo (free) or Google Serper (optional)
"""

import uuid

import structlog
from langchain_core.tools import Tool

from app.config import settings
from app.core.retriever import search_products

logger = structlog.get_logger(__name__)


def _create_web_search_tool() -> Tool:
    """
    Create a web search tool based on the configured provider.
    Defaults to DuckDuckGo (free, no API key) with Serper as an optional upgrade.
    """
    provider = settings.SEARCH_PROVIDER.lower()

    if provider == "serper" and settings.SERPER_API_KEY:
        import os
        os.environ["SERPER_API_KEY"] = settings.SERPER_API_KEY
        from langchain_community.utilities import GoogleSerperAPIWrapper

        search_wrapper = GoogleSerperAPIWrapper()
        logger.info("web_search_tool", provider="serper")

        def serper_search(query: str) -> str:
            return search_wrapper.run(query)

        return Tool(
            name="internet_search",
            func=serper_search,
            description=(
                "Useful for searching real-time information from the internet, "
                "such as latest news, trends, reviews, comparisons, or any "
                "information NOT available in the product database. "
                "Use this when the product database doesn't have the answer."
            ),
        )
    else:
        from langchain_community.tools import DuckDuckGoSearchRun

        search = DuckDuckGoSearchRun()
        logger.info("web_search_tool", provider="duckduckgo")

        def ddg_search(query: str) -> str:
            try:
                return search.run(query)
            except Exception as e:
                logger.warning("duckduckgo_search_failed", query=query, error=str(e))
                return f"Internet search failed due to an error: {e}. Please state that you are unable to perform a web search right now, but provide the best guidance you can without real-time data."

        return Tool(
            name="internet_search",
            func=ddg_search,
            description=(
                "Useful for searching real-time information from the internet, "
                "such as latest news, trends, reviews, comparisons, or any "
                "information NOT available in the product database. "
                "Use this when the product database doesn't have the answer."
            ),
        )


def _create_product_db_tool() -> Tool:
    """Create the product database search tool wrapping the FAISS retriever."""
    logger.info("product_db_tool", provider="faiss")
    return Tool(
        name="product_database_search",
        func=search_products,
        description=(
            "MUST be used FIRST for any product-related queries. "
            "Searches the internal e-commerce product database for product "
            "specifications, descriptions, categories, prices, ratings, and links. "
            "Input should be a natural language search query about products."
        ),
    )


def create_tools() -> list[Tool]:
    """
    Create and return all tools for the ReAct agent.

    Returns:
        List of Tool objects [ProductDatabaseSearch, InternetSearch].
    """
    tools = [
        _create_product_db_tool(),
        _create_web_search_tool(),
    ]
    logger.info("tools_created", count=len(tools), names=[t.name for t in tools])
    return tools
