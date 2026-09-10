"""Shared local Ollama model factory for the validation agents."""

from langchain_ollama import ChatOllama

from app.config import settings


def get_chat_model(model_name: str | None = None, **kwargs) -> ChatOllama:
    """Build a ChatOllama model used by every validation agent."""

    resolved_model_name = model_name or settings.STARTUP_VALIDATOR_MODEL
    return ChatOllama(
        model=resolved_model_name,
        base_url=settings.OLLAMA_BASE_URL,
        **kwargs,
    )
