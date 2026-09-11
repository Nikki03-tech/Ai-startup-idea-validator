"""Shared Gemini model factory with optional API-key rotation."""

import threading

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

_key_index = 0
_key_lock = threading.Lock()


def _configured_keys() -> list[str]:
    """Return configured keys, preferring the comma-separated key pool."""

    if settings.GEMINI_API_KEYS:
        keys = [key.strip() for key in settings.GEMINI_API_KEYS.split(",") if key.strip()]
        if keys:
            return keys

    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        return [settings.GEMINI_API_KEY]

    return []


def _next_api_key() -> str:
    global _key_index
    keys = _configured_keys()
    if not keys:
        raise RuntimeError(
            "No Gemini API key configured. Set GEMINI_API_KEY or "
            "GEMINI_API_KEYS in your .env file."
        )

    with _key_lock:
        api_key = keys[_key_index % len(keys)]
        _key_index += 1
    return api_key


def get_chat_model(model_name: str | None = None, **kwargs) -> ChatGoogleGenerativeAI:
    """Build the Gemini model used by every validation agent."""

    return ChatGoogleGenerativeAI(
        model=model_name or settings.GEMINI_MODEL,
        google_api_key=_next_api_key(),
        max_retries=kwargs.pop("max_retries", 3),
        **kwargs,
    )