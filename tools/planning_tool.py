""" Planning Tool

Task planning and execution tracking utility for agent orchestration.
"""

from typing import Any, Dict, List


def create_execution_plan(tasks: List[str]) -> List[Dict[str, Any]]:
    """
    Build a simple, ordered execution plan for the Orchestrator.

    Each task is represented as a tracked step so the Orchestrator can
    record per-step status ("pending" -> "completed"/"failed") as the
    real LangGraph pipeline (pipeline/graph.py) executes.

    Parameters
    ----------
    tasks:
        Ordered list of task names, e.g.
        ["web_search", "market_analysis", ...].

    Returns
    -------
    A list of plan step dictionaries:
        {"step": 1, "task": "web_search", "status": "pending"}
    """

    return [
        {"step": index, "task": task_name, "status": "pending"}
        for index, task_name in enumerate(tasks, start=1)
    ]
