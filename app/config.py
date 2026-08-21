""" Configuration management for API keys, model settings, and environment variables."""

from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required: used by every agent (ChatGoogleGenerativeAI) and the
    # standalone Orchestrator (google.genai client).
    GEMINI_API_KEY: str

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
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
