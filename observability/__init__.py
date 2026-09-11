"""
Observability package for the AI Startup Idea Validator.
"""

from .metrics import (
    metrics_collector,
    MetricsCollector,
)

from .tracing import (
    trace_agent,
    configure_observability,
)


def get_observability_snapshot() -> dict:
    """Return the current agent timing metrics and summary for app/UI output."""
    return {
        "agent_metrics": metrics_collector.get_metrics(),
        "summary": metrics_collector.get_summary(),
    }


__all__ = [
    "metrics_collector",
    "MetricsCollector",
    "trace_agent",
    "configure_observability",
    "get_observability_snapshot",
]