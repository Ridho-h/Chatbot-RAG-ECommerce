"""
LLM factory — creates the appropriate LangChain chat model
based on the configured provider (Groq or OpenAI).
"""

from langchain_core.language_models.chat_models import BaseChatModel

from app.config import settings


def create_llm() -> BaseChatModel:
    """
    Create and return a chat LLM instance based on application settings.

    Returns:
        BaseChatModel configured for the selected provider.

    Raises:
        ValueError: If the provider is unknown or API key is missing.
    """
    provider = settings.LLM_PROVIDER.lower()

    if provider == "groq":
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
        from langchain_groq import ChatGroq

        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.LLM_MODEL_NAME,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

    else:
        raise ValueError(
            f"Unknown LLM_PROVIDER '{provider}'. Supported: groq, openai"
        )
