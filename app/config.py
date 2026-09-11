""" Configuration management for API keys, model settings, and environment variables."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Gemini model used by every agent and the Orchestrator.
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    STARTUP_VALIDATOR_MODEL: str = "gemini-3.5-flash-lite"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_API_KEYS: Optional[str] = None

    # Optional: not currently wired to any tool (web search runs on
    # DuckDuckGo/ddgs, not Tavily). Kept optional so Settings() doesn't
    # fail for anyone following .env.example, and left available for
    # future Tavily integration.
    TAVILY_API_KEY: Optional[str] = None

    # Matches the remaining variables documented in .env.example.
    SEARCH_ENGINE: str = "duckduckgo"
    MAX_RESULTS: int = 5
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        extra="ignore",
    )


settings = Settings()
