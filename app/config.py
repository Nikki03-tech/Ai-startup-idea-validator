""" Configuration management for API keys, model settings, and environment variables."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Local Ollama model used by every agent and the Orchestrator.
    STARTUP_VALIDATOR_MODEL: str = "llama3.2:1b"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Gemini API key configuration - centralized in app/llm.py, which
    # every agent + the Orchestrator now call instead of reading these
    # directly. Two ways to configure:
    #   - GEMINI_API_KEY alone: single key, unchanged from before.
    #   - GEMINI_API_KEYS (comma-separated): a pool of keys. app/llm.py
    #     automatically rotates to the next key at runtime whenever the
    #     active one hits a quota/rate-limit/auth error, and retries -
    #     no manual index, no restart. GEMINI_API_KEYS takes precedence
    #     over GEMINI_API_KEY when both are set.
    # Optional here (rather than required) so app/llm.py can give a
    # clear, single error message if neither is configured.
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
