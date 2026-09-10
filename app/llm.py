"""Shared Groq model factory for the validation agents."""

import os
from langchain_groq import ChatGroq
from app.config import settings


def get_chat_model(model_name: str | None = None, **kwargs) -> ChatGroq:
    """Build a ChatGroq model used by every validation agent."""

    # 1. Clean up response_format to prevent 400 errors with tool calling
    if "response_format" in kwargs:
        kwargs.pop("response_format")
    
    model_kwargs = kwargs.get("model_kwargs", {})
    if isinstance(model_kwargs, dict) and "response_format" in model_kwargs:
        model_kwargs.pop("response_format", None)

    # 2. Force model to llama-3.1-8b-instant to stay under TPM limits
    resolved_model_name = "llama-3.1-8b-instant"

    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_api_key_here":
        raise RuntimeError(
            "No Groq API key configured. Set GROQ_API_KEY in your .env file."
        )

    return ChatGroq(
        model=resolved_model_name,
        groq_api_key=settings.GROQ_API_KEY,
        max_retries=kwargs.pop("max_retries", 3),
        **kwargs,
    )