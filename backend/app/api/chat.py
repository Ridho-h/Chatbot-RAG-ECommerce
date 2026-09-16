"""
Chat endpoint — the main conversational API.
"""

import time
import uuid

import structlog
from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage

from app.auth.models import User
from app.auth.rbac import get_current_user
from app.core.agent import create_agent_graph
from app.core.llm import create_llm
from app.core.memory import memory_manager
from app.core.tools import create_tools
from app.schemas.chat import ChatRequest, ChatResponse, ProductSource

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Process a chat message and return the agent's response.

    The agent will:
    1. Search the product database for relevant products
    2. Optionally search the internet for additional information
    3. Reason through the results and generate a response
    4. Maintain conversation context via session memory
    """
    start_time = time.perf_counter()

    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())
    history_messages = memory_manager.get_messages(session_id)

    logger.info(
        "chat_request",
        session_id=session_id,
        user=current_user.username,
        message_length=len(request.message),
    )

    try:
        # Create the agent
        llm = create_llm()
        tools = create_tools()
        agent = create_agent_graph(llm, tools)

        # Build input messages: history + new user message
        input_messages = history_messages + [HumanMessage(content=request.message)]

        # Invoke the LangGraph agent with recursion limit
        config = {"recursion_limit": 10}
        result = agent.invoke(
            {"messages": input_messages},
            config=config,
        )

        # Extract the final AI response from the result messages
        output_messages = result.get("messages", [])
        response_text = "I'm sorry, I couldn't process your request."

        # The last message from the agent is the final AI response
        for msg in reversed(output_messages):
            if hasattr(msg, "content") and msg.content and msg.type == "ai":
                # Skip tool call messages (they have tool_calls but may lack text)
                if not getattr(msg, "tool_calls", None):
                    response_text = msg.content
                    break

        # Extract product sources from tool messages
        sources = _extract_sources(output_messages)

        # Save the exchange to session memory
        memory_manager.add_exchange(session_id, request.message, response_text)

    except Exception as e:
        logger.exception("chat_error", session_id=session_id)
        response_text = (
            "I apologize, but I encountered an error processing your request. "
            "Please try again or rephrase your question."
        )
        sources = []

    thinking_time_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "chat_response",
        session_id=session_id,
        user=current_user.username,
        thinking_time_ms=round(thinking_time_ms, 2),
        sources_count=len(sources),
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        sources=sources,
        thinking_time_ms=round(thinking_time_ms, 2),
    )


def _extract_sources(messages: list) -> list[ProductSource]:
    """
    Extract product sources from the agent's tool response messages.
    Parses the formatted retriever output to extract product metadata.
    """
    sources = []
    seen_names = set()

    for msg in messages:
        # Look for tool messages from "product_database_search" or "Product Database Search"
        if getattr(msg, "type", None) == "tool" and getattr(msg, "name", None) in ("product_database_search", "Product Database Search"):
            observation = msg.content if isinstance(msg.content, str) else str(msg.content)
            products = observation.split("--- Product")
            for product_block in products:
                if not product_block.strip():
                    continue
                try:
                    lines = product_block.strip().split("\n")
                    product_data = {}
                    for line in lines:
                        if line.startswith("Name:"):
                            product_data["product_name"] = line.replace("Name:", "").strip()
                        elif line.startswith("Price:"):
                            product_data["discounted_price"] = line.replace("Price:", "").strip()
                        elif line.startswith("Rating:"):
                            # "Rating: 4.5 (1234 reviews)"
                            rating_part = line.replace("Rating:", "").strip()
                            parts = rating_part.split("(")
                            product_data["rating"] = parts[0].strip()
                            if len(parts) > 1:
                                product_data["rating_count"] = parts[1].replace("reviews)", "").replace(")", "").strip()
                        elif line.startswith("Link:"):
                            product_data["product_link"] = line.replace("Link:", "").strip()

                    name = product_data.get("product_name", "")
                    if name and name not in seen_names:
                        seen_names.add(name)
                        sources.append(ProductSource(
                            product_name=product_data.get("product_name", "N/A"),
                            discounted_price=product_data.get("discounted_price", "N/A"),
                            rating=product_data.get("rating", "N/A"),
                            rating_count=product_data.get("rating_count", "N/A"),
                            product_link=product_data.get("product_link", "N/A"),
                        ))
                except (IndexError, KeyError):
                    continue

    return sources
