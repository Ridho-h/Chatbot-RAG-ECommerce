"""
ReAct agent construction using LangGraph's prebuilt create_react_agent.
No runtime dependency on langchain hub — the system prompt is embedded in code.
"""

import uuid
import structlog
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

logger = structlog.get_logger(__name__)

# ── Custom System Prompt ─────────────────────────────────────────────────────
# Guides the LLM to behave as an e-commerce assistant with tool usage rules.

SYSTEM_PROMPT = """You are an intelligent e-commerce shopping assistant. You help customers find products, compare prices, read reviews, and get the best deals.

IMPORTANT RULES:
1. For ANY product-related question, ALWAYS use "product_database_search" FIRST.
2. Search the product database at most ONCE. Do NOT loop or repeatedly search the database with slight query variations.
3. If the product database does NOT contain the requested products (or only contains unrelated items/accessories), you MUST explicitly state that the item is not in our store database. Start your final response with a clear disclaimer (e.g., "I couldn't find this item in our store database, but based on a web search..."), and use "internet_search" to find and suggest options from the broader market.
4. Always provide specific product details when available: name, price, rating, and link.
5. Be helpful, friendly, and concise.
6. Consider the conversation history for context in multi-turn conversations."""


def create_agent_graph(
    llm: BaseChatModel,
    tools: list[Tool],
):
    """
    Create a LangGraph ReAct agent with the given LLM and tools.

    Args:
        llm: The chat language model to use.
        tools: List of tools available to the agent.

    Returns:
        A LangGraph compiled graph ready to process queries.
    """
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )

    logger.info(
        "agent_created",
        tools=[t.name for t in tools],
        agent_type="langgraph_react",
    )

    return agent
