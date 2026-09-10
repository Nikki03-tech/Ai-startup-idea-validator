"""
Guardrails layer for input and final-report validation.
"""

from .validators import (
    validate_startup_input,
    validate_final_report,
)


def validate_input(text: str) -> str:
    """
    Validate and sanitize the user's startup idea.
    """
    return validate_startup_input(text)


def validate_output(text: str) -> str:
    """
    Validate the final validation report.
    """
    return validate_final_report(text)