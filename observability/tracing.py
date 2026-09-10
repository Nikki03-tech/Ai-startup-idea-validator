"""
Local tracing utilities.

Provides lightweight tracing around agent execution.
No external observability platform or API is required.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Iterator

from observability.metrics import (
    start_timer,
    record_agent_metric,
)


logger = logging.getLogger("startup_validator")


@contextmanager
def trace_agent(agent_name: str) -> Iterator[None]:
    """
    Trace one agent execution.

    Records:
    - start
    - completion
    - failure
    - execution duration
    """

    start_time = start_timer()

    logger.info(
        "Agent started: %s",
        agent_name,
    )

    try:
        yield

    except Exception as exc:

        record_agent_metric(
            agent_name=agent_name,
            start_time=start_time,
            status="failed",
            error=str(exc),
        )

        logger.exception(
            "Agent failed: %s",
            agent_name,
        )

        raise

    else:

        record_agent_metric(
            agent_name=agent_name,
            start_time=start_time,
            status="success",
        )

        logger.info(
            "Agent completed: %s",
            agent_name,
        )


def configure_observability() -> None:
    """
    Configure application logging for observability.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )