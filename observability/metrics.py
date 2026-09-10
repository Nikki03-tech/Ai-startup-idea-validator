"""
Local execution metrics for the AI Startup Idea Validator.

Collects:
- execution time
- success/failure
- agent execution count
- errors
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class AgentMetric:
    agent_name: str
    status: str
    duration_seconds: float
    error: str | None = None


class MetricsCollector:
    """
    Process-local metrics collector.

    No external API or monitoring service is required.
    """

    def __init__(self):
        self._metrics: list[AgentMetric] = []
        self._lock = threading.Lock()

    def record(
        self,
        agent_name: str,
        status: str,
        duration_seconds: float,
        error: str | None = None,
    ) -> None:

        metric = AgentMetric(
            agent_name=agent_name,
            status=status,
            duration_seconds=round(duration_seconds, 4),
            error=error,
        )

        with self._lock:
            self._metrics.append(metric)

    def get_metrics(self) -> list[dict[str, Any]]:
        with self._lock:
            return [asdict(metric) for metric in self._metrics]

    def get_summary(self) -> dict[str, Any]:
        with self._lock:
            metrics = list(self._metrics)

        if not metrics:
            return {
                "total_agents": 0,
                "successful_agents": 0,
                "failed_agents": 0,
                "total_execution_time_seconds": 0.0,
            }

        successful = sum(
            1 for metric in metrics
            if metric.status == "success"
        )

        failed = sum(
            1 for metric in metrics
            if metric.status == "failed"
        )

        total_time = sum(
            metric.duration_seconds
            for metric in metrics
        )

        return {
            "total_agents": len(metrics),
            "successful_agents": successful,
            "failed_agents": failed,
            "total_execution_time_seconds": round(total_time, 4),
        }

    def clear(self) -> None:
        with self._lock:
            self._metrics.clear()


# Shared process-level collector
metrics_collector = MetricsCollector()


def start_timer() -> float:
    """Start a high-resolution execution timer."""
    return time.perf_counter()


def record_agent_metric(
    agent_name: str,
    start_time: float,
    status: str,
    error: str | None = None,
) -> None:
    """Record execution metrics for an agent."""

    duration = time.perf_counter() - start_time

    metrics_collector.record(
        agent_name=agent_name,
        status=status,
        duration_seconds=duration,
        error=error,
    )