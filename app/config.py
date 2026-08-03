"""Configuration management for API keys, model settings, and environment variables."""
import os

# Configuration settings
"""Configuration management for API keys, model settings, and environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    TAVILY_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()