"""
Custom deterministic validators for the AI Startup Idea Validator.
"""

import re


SECRET_PATTERNS = [
    r"AIza[0-9A-Za-z_-]{20,}",          # Google/Gemini API key
    r"sk-[A-Za-z0-9_-]{20,}",           # OpenAI-style key
    r"postgresql://[^\s]+",             # PostgreSQL connection string
]


def contains_sensitive_secret(text: str) -> bool:
    """Check whether text contains an API key or database credential."""
    if not isinstance(text, str):
        return False

    return any(
        re.search(pattern, text)
        for pattern in SECRET_PATTERNS
    )


def validate_startup_input(text: str) -> str:
    """Validate user startup idea input."""

    if not isinstance(text, str):
        raise ValueError("Startup idea must be text.")

    text = text.strip()

    if not text:
        raise ValueError("Startup idea cannot be empty.")

    if len(text) > 5000:
        raise ValueError("Startup idea is too long.")

    if contains_sensitive_secret(text):
        raise ValueError(
            "Input contains sensitive credentials or API keys."
        )

    return text


def validate_final_report(text: str) -> str:
    """Validate the final generated validation report."""

    if not isinstance(text, str):
        raise ValueError("Final report must be text.")

    text = text.strip()

    if not text:
        raise ValueError("Final validation report is empty.")

    if contains_sensitive_secret(text):
        raise ValueError(
            "Final report contains sensitive credentials or API keys."
        )

    return text