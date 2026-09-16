"""
Application configuration using Pydantic Settings.
All settings are loaded from environment variables or a .env file.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the Chatbot RAG E-Commerce application."""

    # ── App ──────────────────────────────────────────────────────────────
    APP_NAME: str = "Chatbot RAG E-Commerce"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # ── LLM ──────────────────────────────────────────────────────────────
    LLM_PROVIDER: str = Field(default="groq", description="groq or openai")
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 4096

    # ── Embeddings ───────────────────────────────────────────────────────
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ── Vector Store (Pinecone) ──────────────────────────────────────────
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_INDEX_NAME: str = "ecommerce-bot"
    RETRIEVER_TOP_K: int = 5

    # ── Dataset ──────────────────────────────────────────────────────────
    KAGGLE_USERNAME: Optional[str] = None
    KAGGLE_KEY: Optional[str] = None
    DATASET_NAME: str = "karkavelrajaj/amazon-sales-dataset"
    CSV_FILE_PATH: str = str(Path(__file__).resolve().parent.parent / "data" / "amazon.csv")

    # ── Web Search ───────────────────────────────────────────────────────
    SEARCH_PROVIDER: str = Field(default="duckduckgo", description="duckduckgo or serper")
    SERPER_API_KEY: Optional[str] = None

    # ── Auth / RBAC ──────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-in-production-use-a-strong-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 480  # 8 hours
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"  # Change in production via env var

    # ── Rate Limiting ────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30

    # ── LangSmith Tracing ────────────────────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "ecommerce-chatbot"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # ── Memory ───────────────────────────────────────────────────────────
    MEMORY_WINDOW_SIZE: int = 10  # Number of messages to retain per session
    SESSION_TTL_SECONDS: int = 3600  # 1 hour session expiry

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",
    }


# Singleton instance
settings = Settings()
